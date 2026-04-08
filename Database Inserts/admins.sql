-- USER INSERTS
INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES
(1, 'Michelle', 'Schmidt', 'mschmidt@mona.edu', 'scrypt:32768:8:1$3DFTXoEY7Vqf0CRd$22f1c885c62cca4dad3088bfea6a149ab3cd5d14a11ce4a3569f0038e3049ad79431f7ae161152a8e9d9ae858eea2606134f5ce1108b06c56c8c7dc429623909', 'admin'),
(2, 'Sheila', 'Mcmillan', 'sheila.mcmillan@mona.edu', 'scrypt:32768:8:1$9Byu2Ur2FgJGOJCV$e8a17d5de3454c23e7aacf36c676646026feaee8d939f3a0b5605a2ccdf569e6fa3f20a733ef3762b52f01faaba73f40453afa21e11e226f43491e58b2396aba', 'admin'),
(3, 'John', 'Jones', 'john.jones@mona.edu', 'scrypt:32768:8:1$exRqBm8OzpeSq2Rh$3ea90dfbe10878160ce5a012dd35214cb88a5cc7ba44f98d52ff89e5fe368255a391556f40636adb2df79ee089c8ffea9638202ae5d15d6a2f1267e94bf6ab72', 'admin'),
(4, 'Matthew', 'Williams', 'matthew94@mona.edu', 'scrypt:32768:8:1$pkWffCyA09uXHFAu$191e83c1daf8bd63d632cfbd36916f1eccb9a0ff9c9f0ce0b301e8de2d1e6d88ba071d2289796c0b81bb70535f39a55dd5f387f0ca267633d87a89cfa4b62255', 'admin'),
(5, 'Jamie', 'Wilcox', 'jamie.wilcox@mona.edu', 'scrypt:32768:8:1$VTNHGTQBdI3AuCMk$e35f36f05c743a87bde0e04481b07d6000e5d5afd5841e12003ee17b498b1f3b94ec46a87af5963ea296b776d468b5a017774f54e959216b79e68fa6ac4a1a05', 'admin');

-- ADMIN INSERTS
INSERT INTO Admin (admin_ID, admin_code, user_ID) VALUES
(20533, 'ADM-8716', 1),
(20835, 'ADM-4064', 2),
(20238, 'ADM-5604', 3),
(20777, 'ADM-7476', 4),
(20474, 'ADM-2637', 5);

