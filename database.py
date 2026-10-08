CREATE TABLE IF NOT EXISTS Suppliers (
    Supplier_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Supplier_Name TEXT NOT NULL,
    Phone TEXT,
    Email TEXT
);

CREATE TABLE IF NOT EXISTS Categories (
    Category_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Category_Name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Medicines (
    Medicine_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Medicine_Name TEXT NOT NULL,
    Category_ID INTEGER,
    Supplier_ID INTEGER,
    Batch_No TEXT NOT NULL,
    Quantity INTEGER NOT NULL,
    Price REAL NOT NULL,
    Manufacture_Date TEXT NOT NULL,
    Expiry_Date TEXT NOT NULL,

    FOREIGN KEY (Category_ID)
        REFERENCES Categories(Category_ID),

    FOREIGN KEY (Supplier_ID)
        REFERENCES Suppliers(Supplier_ID)
);

CREATE TABLE IF NOT EXISTS Stock_Transactions (
    Transaction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Medicine_ID INTEGER NOT NULL,
    Transaction_Type TEXT NOT NULL,
    Quantity INTEGER NOT NULL,
    Transaction_Date TEXT NOT NULL,

    FOREIGN KEY (Medicine_ID)
        REFERENCES Medicines(Medicine_ID)
);