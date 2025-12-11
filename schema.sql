-- CS 425 Real Estate Management Application
-- Phase 2
-- Group Memebers:
-- Lohith Gowda Hebbal Patel (A20648331)
-- Suhas Thippesha Gulihatti (A20640633)
-- Susmeet Mitra (A20593956)


select * from information_schema.tables where table_schema = 'public';

CREATE TABLE Users (
    Email VARCHAR(100) PRIMARY KEY,
    First_name VARCHAR(100),
    Address VARCHAR(200)
);

CREATE TABLE Agent (
    Email VARCHAR(100) PRIMARY KEY,
    Job_Title VARCHAR(50),
    Agency VARCHAR(100),
    Phone_Number VARCHAR(20),
	FOREIGN KEY (Email) REFERENCES Users(Email) ON DELETE CASCADE
);

CREATE TABLE Renter (
    Email VARCHAR(100),
    Move_In_Date DATE,
    Preferred_Location VARCHAR(100),
    Budget NUMERIC(12,2),
    PRIMARY KEY (Email),
    FOREIGN KEY (Email) REFERENCES Users(Email) ON DELETE CASCADE
);

CREATE TABLE Neighbourhood (
    Zip_Code VARCHAR(10) PRIMARY KEY,
    Property_Type VARCHAR(50),
    Crime_Rate VARCHAR(50),
    Nearby_Schools TEXT
);


CREATE TABLE Property (
    Property_ID INT PRIMARY KEY,
    Agent_Email VARCHAR(100),
    Zip_Code VARCHAR(10),
    Location VARCHAR(200),
    City VARCHAR(100),
    State VARCHAR(100),
    Price NUMERIC(12,2),
    Availability BOOLEAN,
    Description TEXT,
	FOREIGN KEY (Agent_Email) REFERENCES Users(Email) ON DELETE SET NULL,
	FOREIGN KEY (Zip_Code) REFERENCES Neighbourhood(Zip_Code) ON DELETE SET NULL
);

CREATE TABLE House (
    Property_ID INT,
    Num_of_Rooms INT,
    Square_Feet INT,
	FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
);

CREATE TABLE Apartment (
    Property_ID INT PRIMARY KEY,
    Num_of_Rooms INT,
    Square_Feet INT,
	FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
);

CREATE TABLE CommercialBuilding (
    Property_ID INT PRIMARY KEY,
    Square_Feet INT,
    Business_Type VARCHAR(100),
	FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
);

CREATE TABLE Land (
    Property_ID INT PRIMARY KEY,
    Square_Feet INT,
	FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
);

CREATE TABLE VacationHouse (
    Property_ID INT PRIMARY KEY,
    Square_Feet INT,
    Num_of_Rooms INT,
	FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
);


CREATE TABLE CreditCard (
    Card_Number VARCHAR(20) PRIMARY KEY,
    Card_Holder_Name VARCHAR(100),
    Email VARCHAR(100),
    CVV VARCHAR(4),
    EXP_Date DATE,
    FOREIGN KEY (Email) REFERENCES Renter(Email) ON DELETE CASCADE
);

CREATE TABLE Booking (
    Booking_ID INT PRIMARY KEY,
    Card_Number VARCHAR(20),
    Property_ID INT,
    Booking_Date DATE DEFAULT CURRENT_DATE,
	FOREIGN KEY (Card_Number) REFERENCES CreditCard(Card_Number) ON DELETE CASCADE,
	FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
);

CREATE TABLE Rewards (
    Reward_ID INT PRIMARY KEY,
    Booking_ID INT,
    Email VARCHAR(100),
    Points_Balance INT DEFAULT 0,
	FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID) ON DELETE CASCADE,
	FOREIGN KEY (Email) REFERENCES Renter(Email) ON DELETE CASCADE
);

CREATE TABLE Books (
    Renter_Email VARCHAR(100),
    Property_ID INT,
    PRIMARY KEY (Renter_Email, Property_ID),
	FOREIGN KEY (Renter_Email) REFERENCES Renter(Email) ON DELETE CASCADE,
	FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
);


-- USERS
INSERT INTO Users VALUES
('agent1@gmail.com', 'Ravi Kumar', '12 MG Road, Bengaluru'),
('agent2@gmail.com', 'Sneha Nair', '89 Marine Drive, Kochi'),
('renter1@gmail.com', 'Priya Sharma', '45 Park Street, Kolkata'),
('renter2@gmail.com', 'Amit Verma', '88 Banjara Hills, Hyderabad'),
('renter3@gmail.com', 'Neha Patel', '201 Law Garden, Ahmedabad');

-- AGENT
INSERT INTO Agent VALUES
('agent1@gmail.com', 'Senior Agent', 'DreamHomes India', '9876543210'),
('agent2@gmail.com', 'Property Consultant', 'CityScape Realtors', '9123456789');

-- RENTER
INSERT INTO Renter VALUES
('renter1@gmail.com', '2025-12-01', 'Mumbai', 45000.00),
('renter2@gmail.com', '2026-01-15', 'Bengaluru', 60000.00),
('renter3@gmail.com', '2025-11-20', 'Hyderabad', 40000.00);

-- NEIGHBOURHOOD

INSERT INTO Neighbourhood VALUES
('560001', 'Low', 'Bishop Cotton High, Baldwin Girls High School'),
('400001', 'Medium', 'St. Xavier, Don Bosco High School'),
('500034', 'Low', 'Oakridge International, DPS Hyderabad'),
('600018', 'High', 'DAV Senior Secondary, SBOA School'),
('411001', 'Medium', 'Symbiosis International, St. Mary School');

-- PROPERTY
INSERT INTO Property (Property_ID,Agent_Email, Zip_Code, Location, City, State, Price, Availability, Description) VALUES
(1,'agent1@gmail.com', '560001', '22 Residency Road', 'Bengaluru', 'Karnataka', 9500000.00, TRUE, '3BHK apartment near MG Road'),
(2,'agent2@gmail.com', '400001', '14 Colaba Causeway', 'Mumbai', 'Maharashtra', 12500000.00, TRUE, '4BHK sea-facing flat'),
(3,'renter1@gmail.com', '500034', '101 Jubilee Hills', 'Hyderabad', 'Telangana', 8700000.00, TRUE, '3BHK independent villa'),
(4,'renter2@gmail.com', '600018', '76 T Nagar', 'Chennai', 'Tamil Nadu', 6800000.00, FALSE, '2BHK compact flat'),
(5,'renter3@gmail.com', '411001', '8 FC Road', 'Pune', 'Maharashtra', 7200000.00, TRUE, '3BHK semi-furnished apartment');



-- HOUSE
INSERT INTO House VALUES
(1, 3, 1600),
(2, 4, 2000),
(3, 3, 1800),
(4, 2, 1200),
(5, 3, 1500);

-- APARTMENT
INSERT INTO Apartment VALUES
(1, 3, 1550),
(2, 4, 1900),
(3, 2, 1300),
(4, 3, 1600),
(5, 2, 1250);

-- COMMERCIAL BUILDING
INSERT INTO CommercialBuilding VALUES
(1, 5000, 'IT Office'),
(2, 7000, 'Retail Complex'),
(3, 8000, 'Co-working Space'),
(4, 4500, 'Showroom'),
(5, 6000, 'Restaurant Space');

-- LAND
INSERT INTO Land VALUES
(1, 2400),
(2, 3000),
(3, 2800),
(4, 2000),
(5, 3200);

-- VACATION HOUSE
INSERT INTO VacationHouse VALUES
(1, 2000, 3),
(2, 2500, 4),
(3, 1800, 3),
(4, 2200, 2),
(5, 2600, 4);

-- CREDIT CARD
INSERT INTO CreditCard VALUES
('5555444433332222', 'Priya Sharma', 'renter1@gmail.com', '234', '2027-05-31'),
('4444333322221111', 'Amit Verma', 'renter2@gmail.com', '123', '2026-08-30'),
('9999888877776666', 'Neha Patel', 'renter3@gmail.com', '345', '2028-03-15');

-- BOOKING
INSERT INTO Booking (booking_id, Card_Number, Property_ID, Booking_Date) VALUES
(1,'5555444433332222', 1, '2025-11-01'),
(2,'4444333322221111', 2, '2025-11-02'),
(3,'9999888877776666', 3, '2025-11-03');

-- REWARDS
INSERT INTO Rewards (Reward_ID,Booking_ID, Email, Points_Balance) VALUES
(1,1, 'renter1@gmail.com', 9500),
(2,2, 'renter2@gmail.com', 12500),
(3,3, 'renter3@gmail.com', 8700);

-- BOOKS (optional linking table)
INSERT INTO Books VALUES
('renter1@gmail.com', 1),
('renter2@gmail.com', 2),
('renter3@gmail.com', 3);
