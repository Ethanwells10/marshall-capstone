-- Sample Data for Cross Country Database

-- Insert sample athletes
INSERT INTO athletes (name, grade, personal_record, team) VALUES
('Sarah Johnson', 12, '18:45.20', 'Jones County'),
('Michael Chen', 11, '16:32.15', 'Jones County'),
('Emily Rodriguez', 10, '19:12.45', 'Jones County'),
('David Thompson', 12, '17:08.90', 'Jones County'),
('Jessica Williams', 11, '18:55.30', 'Jones County'),
('Ryan Martinez', 10, '17:45.60', 'Jones County'),
('Amanda Davis', 9, '20:15.75', 'Jones County'),
('Kevin Brown', 12, '16:55.40', 'Jones County');

-- Insert sample meets
INSERT INTO meets (name, date, location, distance) VALUES
('Regional Championship', '2025-10-15', 'Central Park, Columbus', '5K'),
('County Invitational', '2025-09-22', 'Jones County HS', '5K'),
('State Qualifier', '2025-11-01', 'State Fairgrounds', '5K'),
('Fall Classic', '2025-09-08', 'Riverside Trail', '5K'),
('Conference Meet', '2025-10-28', 'Highland Park', '5K');

-- Insert sample results
-- Regional Championship results
INSERT INTO results (athlete_id, meet_id, time, place) VALUES
(2, 1, '16:35.80', 3),   -- Michael Chen
(4, 1, '17:15.25', 8),   -- David Thompson
(8, 1, '17:02.10', 5),   -- Kevin Brown
(1, 1, '18:52.40', 15),  -- Sarah Johnson
(5, 1, '19:05.55', 18),  -- Jessica Williams
(3, 1, '19:25.30', 22),  -- Emily Rodriguez
(6, 1, '17:58.90', 12),  -- Ryan Martinez
(7, 1, '20:45.60', 28);  -- Amanda Davis

-- County Invitational results
INSERT INTO results (athlete_id, meet_id, time, place) VALUES
(2, 2, '16:32.15', 1),   -- Michael Chen (PR!)
(8, 2, '16:55.40', 2),   -- Kevin Brown
(4, 2, '17:10.80', 4),   -- David Thompson
(6, 2, '17:45.60', 9),   -- Ryan Martinez
(1, 2, '18:45.20', 12),  -- Sarah Johnson
(5, 2, '18:55.30', 14),  -- Jessica Williams
(3, 2, '19:12.45', 16),  -- Emily Rodriguez
(7, 2, '20:15.75', 24);  -- Amanda Davis

-- State Qualifier results
INSERT INTO results (athlete_id, meet_id, time, place) VALUES
(2, 3, '16:40.25', 5),   -- Michael Chen
(8, 3, '17:05.70', 10),  -- Kevin Brown
(4, 3, '17:20.45', 12),  -- David Thompson
(6, 3, '18:02.35', 18),  -- Ryan Martinez
(1, 3, '19:00.10', 25),  -- Sarah Johnson
(5, 3, '19:18.85', 28);  -- Jessica Williams

-- Fall Classic results
INSERT INTO results (athlete_id, meet_id, time, place) VALUES
(2, 4, '16:45.90', 2),   -- Michael Chen
(4, 4, '17:25.15', 6),   -- David Thompson
(8, 4, '17:12.30', 4),   -- Kevin Brown
(6, 4, '17:55.40', 11),  -- Ryan Martinez
(1, 4, '19:05.65', 18),  -- Sarah Johnson
(3, 4, '19:35.20', 22),  -- Emily Rodriguez
(5, 4, '19:10.45', 19);  -- Jessica Williams

-- Conference Meet results
INSERT INTO results (athlete_id, meet_id, time, place) VALUES
(2, 5, '16:38.55', 2),   -- Michael Chen
(8, 5, '17:00.85', 7),   -- Kevin Brown
(4, 5, '17:08.90', 8),   -- David Thompson
(6, 5, '17:50.20', 13),  -- Ryan Martinez
(1, 5, '18:58.75', 20),  -- Sarah Johnson
(5, 5, '19:08.40', 23),  -- Jessica Williams
(3, 5, '19:28.90', 26);  -- Emily Rodriguez
