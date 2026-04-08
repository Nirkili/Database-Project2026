DROP DATABASE IF EXISTS University;
CREATE DATABASE University;
USE University;

CREATE TABLE User(
    user_ID INT AUTO_INCREMENT PRIMARY KEY,
    f_name VARCHAR(255) NOT NULL,
    l_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    pswd VARCHAR(255) NOT NULL,
    user_type ENUM('admin', 'lecturer', 'student')
);

CREATE TABLE Student(
    st_ID INT PRIMARY KEY,
    user_ID INT,

    FOREIGN KEY (user_ID)
    REFERENCES User(user_ID) 
    ON DELETE CASCADE    
);

CREATE TABLE Lecturer(
    lect_ID INT PRIMARY KEY,
    dept VARCHAR(100),
    user_ID INT,

    FOREIGN KEY (user_ID)
    REFERENCES User(user_ID) 
    ON DELETE CASCADE 
);


CREATE TABLE Admin(
    admin_ID INT PRIMARY KEY,
    admin_code VARCHAR(100),
    user_ID INT,

    FOREIGN KEY (user_ID)
    REFERENCES User(user_ID) 
    ON DELETE RESTRICT
);


CREATE TABLE Course(
    c_code VARCHAR(15) PRIMARY key, 
    c_name VARCHAR(150),
    c_credits INT,
    dept VARCHAR(50),
    lect_ID INT,
    admin_ID INT NOT NULL,
    
    FOREIGN KEY (lect_ID)
    REFERENCES Lecturer(lect_ID) 
    ON DELETE RESTRICT,
    
    FOREIGN KEY (admin_ID) 
    REFERENCES Admin(admin_ID) 
    ON DELETE CASCADE
);

CREATE TABLE Assignment(
        a_ID INT AUTO_INCREMENT PRIMARY KEY,
        a_desc TEXT,
        a_due_date DATE,
        c_code VARCHAR(15),

        FOREIGN KEY (c_code)
        REFERENCES Course(c_code) 
        ON DELETE CASCADE
);

CREATE TABLE Forum(
    forum_ID INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100),
    date_created DATE,
    c_code VARCHAR(15),

    FOREIGN KEY (c_code)
    REFERENCES Course(c_code) 
    ON DELETE CASCADE
);

CREATE TABLE Thread(
    t_ID INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    user_ID INT,
    forum_ID INT,
    parent_ID INT NULL,

    FOREIGN KEY (user_ID)
    REFERENCES User(user_ID) 
    ON DELETE CASCADE,

    FOREIGN KEY (forum_ID) 
    REFERENCES Forum(forum_ID) 
    ON DELETE CASCADE,
    
     FOREIGN KEY (parent_ID) 
     REFERENCES Thread(t_ID) 
     ON DELETE CASCADE
);

CREATE TABLE CalendarEvent(
    event_ID INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(100),
    details TEXT,
    event_date DATE,
    c_code VARCHAR(15),
    
    FOREIGN KEY (c_code)
    REFERENCES Course(c_code) 
    ON DELETE CASCADE

);

CREATE TABLE Section(
    section_ID INT AUTO_INCREMENT PRIMARY KEY,
    sect_title VARCHAR(100),
    sect_name VARCHAR(100),
    c_code VARCHAR(15),

    FOREIGN KEY (c_code)
    REFERENCES Course(c_code) 
    ON DELETE CASCADE
);

CREATE TABLE CourseContent(
    con_id INT AUTO_INCREMENT PRIMARY KEY,
    con_type ENUM('link', 'file', 'slide'),
    con_desc TEXT,
    file_name VARCHAR(255),
    sect_ID INT,

    FOREIGN KEY (sect_ID)
    REFERENCES Section(section_ID)
);


/*---- RELATIONSHIP TABLES ----*/
CREATE TABLE Register_for(
    st_ID INT,
    c_code VARCHAR(15),
    final_avg INT,

    PRIMARY KEY(st_ID, c_code),

    FOREIGN KEY (c_code)
    REFERENCES Course(c_code) 
    ON DELETE CASCADE,

    FOREIGN KEY (st_ID)
    REFERENCES Student(st_ID) 
    ON DELETE CASCADE
);

CREATE TABLE Submits(
    sub_date DATE,
    grade INT,
    a_ID INT,
    st_ID INT,
    
    PRIMARY KEY (a_ID, st_ID),

    FOREIGN KEY (st_ID)
    REFERENCES Student(st_ID) 
    ON DELETE CASCADE,

    FOREIGN KEY (a_ID) 
    REFERENCES Assignment(a_ID) 
    ON DELETE CASCADE
);

/* Views */

CREATE VIEW PopularCourses AS 
SELECT c_code, COUNT(st_ID) AS total_students
FROM Register_for 
GROUP BY c_code
HAVING COUNT(st_ID) >= 50;


CREATE VIEW OverwhelmedStudents AS
SELECT st_ID, COUNT(c_code) AS total_courses
FROM Register_for
GROUP BY st_ID
HAVING COUNT(c_code) >= 5;


CREATE VIEW BusyLecturers AS
SELECT lect_ID, COUNT(c_code) AS total_courses
FROM Course
GROUP BY lect_ID
HAVING COUNT(c_code) >= 3;

CREATE VIEW TopCourses AS
SELECT c_code, COUNT(st_ID) AS total_students
FROM Register_for
GROUP BY c_code
ORDER BY total_students DESC
LIMIT 10;

CREATE VIEW TopStudents AS
SELECT st_ID, AVG(final_avg) AS avg_score
FROM Register_for
GROUP BY st_ID
ORDER BY avg_score DESC
LIMIT 10;

