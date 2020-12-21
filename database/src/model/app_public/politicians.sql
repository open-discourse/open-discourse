CREATE TABLE app_public.politicians (
	id int8 NOT NULL,
	first_name varchar NOT NULL,
	last_name varchar NOT NULL,
	birth_place varchar NULL,
	birth_country varchar NULL,
	birth_date date NULL,
	death_date date NULL,
	gender varchar NULL,
	profession varchar NULL,
	aristocracy varchar NULL,
	academic_title varchar NULL,
	CONSTRAINT mdbs_pk PRIMARY KEY (id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.politicians TO visitor;
