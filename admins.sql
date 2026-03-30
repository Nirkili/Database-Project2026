-- USER INSERTS
INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES
(1, 'Kelly', 'Beltran', 'kelly41@mona.edu', SHA2('##&13BoXcv', 256), 'admin'),
(2, 'George', 'Alvarez', 'galvarez@mona.edu', SHA2('_rKp7qwkM8', 256), 'admin'),
(3, 'Raymond', 'Sanford', 'rsanford@mona.edu', SHA2('%I87Bzd662', 256), 'admin'),
(4, 'Christopher', 'Allen', 'christopher54@mona.edu', SHA2('(_1AQmGEB_', 256), 'admin'),
(5, 'Tyler', 'Wright', 'twright@mona.edu', SHA2('e)sO8Zok%#', 256), 'admin');

-- ADMIN INSERTS
INSERT INTO Admin (admin_ID, admin_code, user_ID) VALUES
(20504, 'ADM-2055', 1),
(20238, 'ADM-2816', 2),
(20334, 'ADM-6970', 3),
(20172, 'ADM-4005', 4),
(20495, 'ADM-7419', 5);
