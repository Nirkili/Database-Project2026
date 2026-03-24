DROP DATABASE IF EXISTS University;
CREATE DATABASE University;
USE University; 

CREATE TABLE User(
    user_ID INT PRIMARY KEY,
    f_name VARCHAR(255) NOT NULL,
    l_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    pswd VARCHAR(255) NOT NULL
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
    faculty VARCHAR(100),
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
    lect_ID INT,
    admin_ID INT,
    
    FOREIGN KEY (lect_ID)
    REFERENCES Lecturer(lect_ID) 
    ON DELETE RESTRICT,
    
    FOREIGN KEY (admin_ID) 
    REFERENCES Admin(admin_ID) 
    ON DELETE CASCADE
);

CREATE TABLE Assignment(
        a_ID INT PRIMARY KEY,
        a_desc TEXT,
        a_due_date DATE,
        c_code VARCHAR(15),

        FOREIGN KEY (c_code)
        REFERENCES Course(c_code) 
        ON DELETE CASCADE
);

CREATE TABLE Forum(
    forum_ID INT PRIMARY KEY,
    title VARCHAR(100),
    date_created DATE,
    c_code VARCHAR(15),

    FOREIGN KEY (c_code)
    REFERENCES Course(c_code) 
    ON DELETE CASCADE
);

CREATE TABLE Thread(
    t_ID INT PRIMARY KEY,
    content TEXT,
    user_ID INT,
    forum_ID INT,

    FOREIGN KEY (user_ID)
    REFERENCES User(user_ID) 
    ON DELETE CASCADE,

    FOREIGN KEY (forum_ID) 
    REFERENCES Forum(forum_ID) 
    ON DELETE CASCADE
);

CREATE TABLE CalendarEvent(
    event_ID INT PRIMARY KEY,
    event_name VARCHAR(100),
    details TEXT,
    c_code VARCHAR(15),
    
    FOREIGN KEY (c_code)
    REFERENCES Course(c_code) 
    ON DELETE CASCADE

);

CREATE TABLE Section(
    section_ID INT PRIMARY KEY,
    sect_title VARCHAR(100),
    sect_name VARCHAR(100),
    c_code VARCHAR(15),

    FOREIGN KEY (c_code)
    REFERENCES Course(c_code) 
    ON DELETE CASCADE
);

CREATE TABLE CourseContent(
    con_id INT PRIMARY KEY,
    con_type VARCHAR(20),
    con_desc TEXT,
    file_name VARCHAR(50),
    sect_ID INT,

    FOREIGN KEY (sect_ID)
    REFERENCES Section(section_ID)
);


---- RELATIONSHIP TABLES ----
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


CREATE TABLE Replies(
    parent_t_ID INT,
    child_t_ID INT,

    PRIMARY KEY(parent_t_ID, child_t_ID),

    FOREIGN KEY (parent_t_ID)
    REFERENCES Thread(t_ID)
    ON DELETE CASCADE,

    FOREIGN KEY (child_t_ID)
    REFERENCES Thread(t_ID) 
    ON DELETE CASCADE
);





