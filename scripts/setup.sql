-- Setup Script for the Native Application
CREATE APPLICATION ROLE IF NOT EXISTS APP_PUBLIC;

-- create a new versioned schema to be used for public objects
CREATE OR ALTER VERSIONED SCHEMA app_schema;
GRANT USAGE ON SCHEMA app_schema TO APPLICATION ROLE APP_PUBLIC;

-- use tables from the application package and create views in the app
CREATE OR REPLACE VIEW app_schema.CPIVSFEDFUNDS AS SELECT * FROM shared_data.CPIVSFEDFUNDS;

-- grant select on the views to APP_PUBLIC role so the consumer can access them
GRANT SELECT ON VIEW app_schema.CPIVSFEDFUNDS TO APPLICATION ROLE APP_PUBLIC;

-- add Streamlit object
CREATE OR REPLACE STREAMLIT app_schema.streamlit
  FROM '/streamlit'
  MAIN_FILE = '/inflation_data.py'
;

-- grant APP_PUBLIC role to access the Streamlit object
GRANT USAGE ON STREAMLIT app_schema.streamlit TO APPLICATION ROLE APP_PUBLIC;