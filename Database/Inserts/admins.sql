-- USER INSERTS
INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES
(1, 'Scott', 'Williams', 'scott36@mona.edu', 'scrypt:32768:8:1$L4ErhCNALxRh5kSg$78882891c58e552d884a3a9f45130ff051be170675efcc364d2cd549daf131d6a99eedcf61221e06233c58a88e7718e20062a89ae330dfe450a8ead451751c6c', 'admin'),
(2, 'Jenny', 'Johnson', 'jenny.johnson@mona.edu', 'scrypt:32768:8:1$2li1kQlr0Ld0T3YE$d192f49f311825a8675bbfa2bf35d9380b509219393e4272fe5be04514cf4743d4334ddb4ed32c42c469aa1b2ea7e5d3cd88a6fb035a9fc4ab2521d085a86fbe', 'admin'),
(3, 'Thomas', 'Lewis', 'tlewis@mona.edu', 'scrypt:32768:8:1$DbarMRxgVZsZxqL9$1bd02792fa92548c203a496dc55878d48fbfe9e27f3940dc10b64e006aba9f7540100015522518ba21e27c6f0716cba02989f7f0e91b0dfc8c28e0789eb5fede', 'admin'),
(4, 'Cindy', 'Santiago', 'csantiago@mona.edu', 'scrypt:32768:8:1$K6Uymsl8a3aHpooh$93b3cb9049501f2d8b589316f63ab012038ac40e8cdec4bcf3f344f0cb0cbaa01884a90130d24eb9209c1130efcf75187642e773499ac21e82ae224ae2c358d6', 'admin'),
(5, 'Christine', 'Brown', 'christine93@mona.edu', 'scrypt:32768:8:1$fRCreecfJdrLOLVH$deddb8beddd7cbccf384beed80a998cfe979e550bcff194315581142686ef44193827e37b9abd4a67bce923e44fc89a3566f297b34cb948d653456a8e8447b79', 'admin');

-- ADMIN INSERTS
INSERT INTO Admin (admin_ID, admin_code, user_ID) VALUES
(20856, 'ADM-7967', 1),
(20704, 'ADM-7593', 2),
(20941, 'ADM-8792', 3),
(20877, 'ADM-5645', 4),
(20542, 'ADM-5173', 5);

