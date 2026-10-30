# Task3 - Reverse Engineering

## AI Answer1:

AI Answer 1: What is the difference between SELECT SINGLE and SELECT UP TO 1 ROWS in SAP ABAP?

Both statements are used to retrieve a single record from a database table, but they have some differences.



SELECT SINGLE

SELECT UP TO 1 ROWS

Retrieves one matching record

Retrieves at most one record

Does not support ORDER BY

Supports ORDER BY

Useful for retrieving a record using a unique key

Useful when you need a specific record based on sorting

Example:

abap

SELECT SINGLE \*

&#x20; FROM mara

&#x20; INTO @DATA(ls\_material)

&#x20; WHERE matnr = '100001'.

abap

SELECT \*

&#x20; FROM mara

&#x20; INTO TABLE @DATA(lt\_material)

&#x20; UP TO 1 ROWS

&#x20; ORDER BY matnr DESCENDING.

Conclusion: Use SELECT SINGLE when retrieving a record using a unique condition. Use UP TO 1 ROWS when you need more control over which record is selected through sorting.



## Prompt1 :

Act as an SAP ABAP interviewer and answer this question the way a strong candidate would: "What is the difference between SELECT SINGLE and SELECT UP TO 1 ROWS?" Keep it concise, use a table for the differences, include example code, and end with a one-line conclusion.



## Answer:

Interviewer’s question: What is the difference between SELECT SINGLE and SELECT UP TO 1 ROWS?

Both return one record, but they differ in how the database handles the query and which record you get.



Aspect	SELECT SINGLE	SELECT UP TO 1 ROWS

Purpose	Fetch one specific record, ideally via the full primary key	Fetch the first record matching a condition, when many may exist

Full key needed?	Should specify all key fields (otherwise the syntax check warns)	No, any WHERE condition works

Which record?	Arbitrary if the key is incomplete	Can be controlled with ORDER BY

ORDER BY	Not allowed	Allowed (sorts, then returns the top row)

Closing statement	None	Needs ENDSELECT when using a work area (not with INTO TABLE)

Database behavior	Reads one row, no cursor	Opens a cursor, stops after 1 row

Buffering	Works well with table buffering	Bypasses single-record buffering

Typical use	Master data lookup, e.g. a material or customer by key	“Latest” or “first” record, e.g. most recent invoice for a customer





abap

" 1. SELECT SINGLE - full primary key, exact record

SELECT SINGLE vbeln, fkdat, netwr

&#x20; FROM vbrk

&#x20; INTO @DATA(ls\_invoice)

&#x20; WHERE vbeln = @lv\_vbeln.



" 2. UP TO 1 ROWS - partial condition, with ORDER BY

SELECT vbeln, fkdat, netwr

&#x20; FROM vbrk

&#x20; WHERE kunag = @lv\_customer

&#x20; ORDER BY fkdat DESCENDING

&#x20; INTO TABLE @DATA(lt\_latest)

&#x20; UP TO 1 ROWS.



READ TABLE lt\_latest INTO DATA(ls\_latest) INDEX 1.



Follow-up point a strong candidate would add: with SELECT SINGLE on a non-key condition, the result is not guaranteed to be the same every time, which is a classic source of unpredictable bugs. If you need “first” or “latest”, UP TO 1 ROWS with ORDER BY is the correct choice.



Conclusion: Use SELECT SINGLE when you know the full key and want a unique record; use UP TO 1 ROWS (with ORDER BY) when several records could match and you need a deterministic one.





## AI Answer2:

How to Create a Transparent Table in SAP ABAP

A Transparent Table is a database table created in the ABAP Dictionary (SE11). It stores application data permanently in the SAP database.



Step-by-step procedure

Step

Action

Explanation

1.Open SE11

&#x20;Enter transaction code SE11 in SAP GUI.

2.select Database Table

Choose the Database Table option.

3.Enter table name

Enter ZEMPLOYEE and click Create.

4.Add description

Enter Employee Details as the short description.

5.Define fields

Add fields such as EMP\_ID, EMP\_NAME and DEPARTMENT.

6.Assign Data Elements

Assign suitable Data Elements to each field.

7.Set primary key

Mark EMP\_ID as the key field.

8.Maintain technical settings

Configure the data class and size category as appropriate.

9.Save the table

Assign the required development package or local object.

10.Activate

Check and activate the table.



Example table structure

Field nam Key Data Element

MANDT Yes MANDT

EMP\_ID Yes ZDE\_EMP\_ID

EMP\_NAME No ZDE\_EMP\_NAME

DEPARTMENT No ZDE\_DEPARTMENT



Important points

Every table needs a valid technical definition.

Data Elements provide field-level semantic information.

Primary key fields uniquely identify table records.

The table must be activated before it can be used in ABAP programs.

Avoid using unnecessary key fields.



Common mistakes to avoid

Forgetting to define key fields.

Assigning incorrect Data Elements.

Not maintaining technical settings.

Forgetting to activate the table.



Conclusion: A Transparent Table can be created through SE11 by defining its fields, assigning Data Elements, maintaining technical settings, and activating it.

## 

## Prompt-2   :

Act as an SAP ABAP trainer and explain "How to create a Transparent Table in SAP ABAP" for a beginner.



Structure the answer like this:

1\. A short definition of a Transparent Table (one or two lines).

2\. A step-by-step procedure in a table with three columns: Step, Action, Explanation. Cover SE11, table name, description, fields, data elements, primary key, technical settings, saving, and activation.

3\. An example table structure in a table with columns: Field name, Key, Data Element. Use ZEMPLOYEE with MANDT, EMP\_ID, EMP\_NAME and DEPARTMENT.

4\. A short "Important points" bullet list.

5\. A short "Common mistakes to avoid" bullet list.

6\. End with a one-line conclusion.



Keep the language simple and concise.



## Answer:



How to Create a Transparent Table in SAP ABAP

1\. Definition



A Transparent Table is a database table in the SAP Data Dictionary that has a one-to-one match with a physical table in the database. It stores application data permanently, with the same name and fields in both SAP and the database.



2\. Step-by-Step Procedure

Step	Action	Explanation

1	Go to transaction SE11	SE11 is the ABAP Dictionary, where tables, data elements and domains are created.

2	Select Database table, enter the table name (e.g., ZEMPLOYEE) and click Create	Custom tables must start with Z or Y so they don’t clash with SAP standard objects.

3	Enter a Short Description	A short text explaining the purpose of the table, e.g., “Employee Master Table”.

4	On the Delivery and Maintenance tab, set the Delivery Class to A	Class A means application table (master and transaction data).

5	Go to the Fields tab and enter the field names	Each column of the table is defined here, e.g., MANDT, EMP\_ID, EMP\_NAME, DEPARTMENT.

6	Assign a Data Element (or predefined type) to each field	The data element gives the field its data type, length and description.

7	Tick the Key checkbox for the primary key fields	Key fields uniquely identify each record. For client-dependent tables, MANDT is always a key field.

8	Go to Technical Settings (Menu: Goto → Technical Settings)	Set Data Class (APPL0 for master data, APPL1 for transaction data), Size Category (0 to 4, based on expected number of records), and Buffering (usually “Buffering not allowed” or as needed). Then save.

9	Save the table (Ctrl+S)	Assign a package (or use $TMP for local objects) and a transport request if needed.

10	Activate the table (Ctrl+F3)	The table is created in the database only after activation. Check the log for errors.



3\. Example Table Structure: ZEMPLOYEE

Field name	Key	Data Element

MANDT	✔	MANDT

EMP\_ID	✔	ZEMP\_ID (or NUMC8)

EMP\_NAME		ZEMP\_NAME (or CHAR40)

DEPARTMENT		ZDEPARTMENT (or CHAR20)



4\. Important Points

Table names must start with Z or Y for custom objects.

MANDT (client) should be the first field and a key field for client-dependent tables.

Key fields must be placed at the top, with no non-key field between them.

The table must be activated before it can be used in programs.

Use SE16 / SE16N to view and test table data after activation.

Data elements can be reused, so create them once and use them across tables.

5\. Common Mistakes to Avoid

Forgetting to set Technical Settings, which causes an activation error.

Not marking any field as a Key.

Missing the MANDT field in client-dependent tables.

Forgetting to activate the table after saving.

Using non-Z/Y names for custom tables.

Leaving the Delivery Class blank.

6\. Conclusion



A Transparent Table is created in SE11 by defining fields, keys and technical settings, and it only becomes usable after activation.



## AI Answer-3:

What is the difference between BAPI and RFC in SAP ABAP?

BAPI (Business Application Programming Interface) and RFC (Remote Function Call) are used in SAP ABAP to enable communication between different SAP systems or external applications. However, they have different purposes and functionalities.



1\. What is RFC?

RFC stands for Remote Function Call. It allows a function module to be executed in another SAP system or an external system.



Example:

abap

CALL FUNCTION 'Z\_GET\_EMPLOYEE'

&#x20; DESTINATION 'NONE'

&#x20; EXPORTING

&#x20;   employee\_id = '1001'

&#x20; IMPORTING

&#x20;   employee\_name = lv\_name.

Here, RFC is used to call a function module remotely.



2\. What is BAPI?

BAPI stands for Business Application Programming Interface. It is a standardized interface that allows external applications or other SAP systems to access SAP business processes and data.



Example:

abap

CALL FUNCTION 'BAPI\_USER\_GET\_DETAIL'

&#x20; EXPORTING

&#x20;   username = 'TESTUSER'

&#x20; IMPORTING

&#x20;   address  = ls\_address

&#x20; TABLES

&#x20;   return   = lt\_return.

Here, a standard BAPI is used to retrieve SAP user details.



3\. Difference between BAPI and RFC

Feature

BAPI

RFC

Full form

Business Application Programming Interface

Remote Function Call

Purpose

Access SAP business processes and data

Execute function modules remotely

Standardization

Follows standardized business interfaces

Can be custom-developed or standard

Functionality

Represents a business operation

Provides remote function execution

Usage

Used for business transactions and integration

Used for communication between systems

Communication

Uses RFC technology for remote access

Enables remote function execution



4\. When should we use BAPI and RFC?

Use BAPI when:

You want to perform standard SAP business operations.

You need a standardized interface.

You want to integrate external applications with SAP business processes.

Use RFC when:

You want to execute a function module remotely.

You need custom communication between SAP systems.

You want to exchange data between different systems.



5\. Important points to remember

BAPIs are implemented as RFC-enabled function modules.

Every RFC is not a BAPI.

BAPIs follow standardized business object interfaces.

RFC is the underlying communication mechanism that can support BAPI calls.

Conclusion: BAPI is a standardized business interface used to access SAP business functionality, whereas RFC is a communication mechanism used to execute function modules remotely.



## Prompt3:

Act as an SAP ABAP trainer and explain "the difference between BAPI and RFC in SAP ABAP" for a beginner. Structure the answer like this:



1\. A short introduction (two lines) saying what BAPI and RFC are used for.

2\. "What is RFC?" with a one-line definition and a small ABAP code example.

3\. "What is BAPI?" with a one-line definition and a small ABAP code example using a standard BAPI.

4\. "Difference between BAPI and RFC" in a table with columns: Feature, BAPI, RFC. Cover full form, purpose, standardization, functionality, usage and communication.

5\. "When should we use BAPI and RFC?" with two short bullet lists.

6\. "Important points to remember" as a short bullet list.

7\. End with a one-line conclusion.



Keep the language simple and concise.

