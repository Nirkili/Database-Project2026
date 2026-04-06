-- USER INSERTS
INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES
(1, 'Shelley', 'Joseph', 'shelley.joseph@mona.edu', SHA2('bT6TM*$c+a', 256), 'admin'),
(2, 'Derek', 'Howe', 'dhowe@mona.edu', SHA2('!7TTLG@hVF', 256), 'admin'),
(3, 'Frank', 'Payne', 'fpayne@mona.edu', SHA2('(&1hSQon04', 256), 'admin'),
(4, 'Jennifer', 'Quinn', 'jennifer.quinn@mona.edu', SHA2('taFAm2vJ+0', 256), 'admin'),
(5, 'Judith', 'Norris', 'jnorris@mona.edu', SHA2('o0b4WhOt*l', 256), 'admin');

-- ADMIN INSERTS
INSERT INTO Admin (admin_ID, admin_code, user_ID) VALUES
(20840, 'ADM-3730', 1),
(20173, 'ADM-2886', 2),
(20044, 'ADM-6982', 3),
(20930, 'ADM-7410', 4),
(20149, 'ADM-4222', 5);

