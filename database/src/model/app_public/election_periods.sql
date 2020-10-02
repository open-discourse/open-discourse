CREATE TABLE app_public.election_periods (
	id int8 NOT NULL,
	"start_date" int8 NOT NULL,
	"end_date" int8 NULL,
	CONSTRAINT election_periods_pk PRIMARY KEY (id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.election_periods TO visitor;
