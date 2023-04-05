# ΔΙΑΔΙΚΤΥΟ ΤΩΝ ΠΡΑΓΜΑΤΩΝ
# ΟΜΑΔΙΚΗ ΕΡΓΑΣΤΗΡΙΑΚΗ ΕΡΓΑΣΙΑ
# ΕΞΥΠΝΟΣ ΦΩΤΙΣΜΟΣ

# Τόμτσης Θωμάς, 321/2015201
# Ζαγαλιώτη Φωτεινή, 321/2019054
# Κυριακίδης Δημοσθένης, 321/2019102

# Υλοποίηση : Τόμτσης Θωμάς


# Δημιουργία της ΒΔ
DROP DATABASE IF EXISTS ttn_msg;
CREATE DATABASE ttn_msg;
USE ttn_msg;

# Δημιουργία χρήστη
DROP USER IF EXISTS 'iot'@'localhost';
CREATE USER 'iot'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'iot'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# Δημιουργία Πινάκων
DROP TABLE IF EXISTS uplink;
DROP TABLE IF EXISTS downlink;

CREATE TABLE uplink (
  id int NOT NULL UNIQUE auto_increment,
  topic varchar(70) NOT NULL,
  device_id varchar(70) NOT NULL,
  application_id varchar(70) NOT NULL,
  dev_eui varchar(150) NOT NULL,
  join_eui varchar(150) NOT NULL,
  received varchar(200),
  fport int,
  frm_payload varchar(50),
  decoded_payload varchar(50),
  PRIMARY KEY (id)
);

CREATE TABLE downlink (
  id int NOT NULL UNIQUE auto_increment,
  topic varchar(70) NOT NULL,
  device_id varchar(70) NOT NULL,
  application_id varchar(70) NOT NULL,
  fport int,
  frm_payload varchar(50),
  decoded_payload varchar(50),
  PRIMARY KEY (id)
);