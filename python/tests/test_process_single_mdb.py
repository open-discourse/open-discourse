import xml.etree.ElementTree as Et
from collections import namedtuple

import pytest

from open_discourse.steps.preprocessing.extract_mps_from_mp_base_data import (
    process_single_mdb,
)

# Definition Named Tuple for test cases, don't name ist Testcase!!!
CaseDataforTest = namedtuple("CaseDataforTest", ["input", "expected", "exception"])

# RAW_XML = path_definitions.RAW_XML
# RAW_TXT = path_definitions.RAW_TXT

# ========================================
# test cases for process_single_mdb (list of namedtuple)
# ========================================
test_cases = []
################

xml_string = """	<MDB>
		<ID>11005229</ID>
		<NAMEN>
			<NAME>
				<NACHNAME>Stegner</NACHNAME>
				<VORNAME>Ralf</VORNAME>
				<ORTSZUSATZ/>
				<ADEL/>
				<PRAEFIX/>
				<ANREDE_TITEL>Dr.</ANREDE_TITEL>
				<AKAD_TITEL>Dr.</AKAD_TITEL>
				<HISTORIE_VON>26.10.2021</HISTORIE_VON>
				<HISTORIE_BIS/>
			</NAME>
		</NAMEN>
		<BIOGRAFISCHE_ANGABEN>
			<GEBURTSDATUM>02.10.1959</GEBURTSDATUM>
			<GEBURTSORT>Bad Dürkheim</GEBURTSORT>
			<GEBURTSLAND/>
			<STERBEDATUM/>
			<GESCHLECHT>männlich</GESCHLECHT>
			<FAMILIENSTAND>verheiratet, 3 Kinder</FAMILIENSTAND>
			<RELIGION>evangelisch</RELIGION>
			<BERUF>Politikwissenschaftler</BERUF>
			<PARTEI_KURZ>SPD</PARTEI_KURZ>
			<VITA_KURZ>1978 Abitur. 1980/87 Studium Politikwissenschaft, Geschichte und  Deutsch Univ. Freiburg, 1983/87 Stipendiat der Friedrich-Ebert-Stiftung, 1984/85 Studium University of Oregon in Eugene/Oregon (USA), 1987/89 McCloy-Scholar der Stiftung Volkswagenwerk und Studienstiftung des dt. Volkes Harvard Universität in Cambridge MA. (USA), 1989 Master of Public Administration der Kennedy School of Government der Harvard Universität. 1990/94 Referent für Presse- und Öffentlichkeitsarbeit Ministerium für Arbeit, Soziales, Jugend und Gesundheit des Landes Schleswig-Holstein, 1992 Promotion Univ. Hamburg, 1994/96 Leiter Stabsbereich bei der Sozialministerin. Mitgl. der SPD seit 1982, 1998/2002 stellv. Kreisvors. Rendsburg-Eckernförde, versch. Funktionen in den Kreisen Pinneberg und Rendsburg-Eckernförde, 2007/19 Vors. SPD Schleswig-Holstein, 2014/19 stellv. Vors. der SPD. Mai 1996/Okt. 1998 Staatssekretär im Ministerium für Arbeit, Soziales, Jugend und Gesundheit, Okt. 1998/März 2003 im Ministerium für Bildung, Wissenschaft, Forschung und Kultur, März 2003/April 2005 Finanzminister des Landes Schleswig-Holstein, April 2005/Jan. 2008 Innenminister des Landes Schleswig-Holstein. MdL Schleswig-Holstein März 2005/Okt. 2021, ab Jan. 2008 Vors. der SPD-Fraktion. - MdB seit Okt. 2021.</VITA_KURZ>
			<VEROEFFENTLICHUNGSPFLICHTIGES/>
		</BIOGRAFISCHE_ANGABEN>
		<WAHLPERIODEN>
			<WAHLPERIODE>
				<WP>20</WP>
				<MDBWP_VON>26.10.2021</MDBWP_VON>
				<MDBWP_BIS/>
				<WKR_NUMMER>7</WKR_NUMMER>
				<WKR_NAME>Pinneberg</WKR_NAME>
				<WKR_LAND>SH</WKR_LAND>
				<LISTE/>
				<MANDATSART>Direktwahl</MANDATSART>
				<INSTITUTIONEN>
					<INSTITUTION>
						<INSART_LANG>Fraktion/Gruppe</INSART_LANG>
						<INS_LANG>Fraktion der Sozialdemokratischen Partei Deutschlands</INS_LANG>
						<MDBINS_VON>26.10.2021</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG/>
						<FKTINS_VON/>
						<FKTINS_BIS/>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Ausschuss</INSART_LANG>
						<INS_LANG>Auswärtiger Ausschuss</INS_LANG>
						<MDBINS_VON>15.12.2021</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG>Ordentliches Mitglied</FKT_LANG>
						<FKTINS_VON>15.12.2021</FKTINS_VON>
						<FKTINS_BIS/>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Ausschuss</INSART_LANG>
						<INS_LANG>Ausschuss für die Angelegenheiten der Europäischen Union</INS_LANG>
						<MDBINS_VON>15.12.2021</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG>Stellvertretendes Mitglied</FKT_LANG>
						<FKTINS_VON>15.12.2021</FKTINS_VON>
						<FKTINS_BIS/>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Ausschuss</INSART_LANG>
						<INS_LANG>Ausschuss für Inneres und Heimat</INS_LANG>
						<MDBINS_VON>15.12.2021</MDBINS_VON>
						<MDBINS_BIS>08.11.2023</MDBINS_BIS>
						<FKT_LANG>Stellvertretendes Mitglied</FKT_LANG>
						<FKTINS_VON>15.12.2021</FKTINS_VON>
						<FKTINS_BIS>08.11.2023</FKTINS_BIS>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Sonstiges Gremium</INSART_LANG>
						<INS_LANG>Mitglieder im Parlamentarischen Kontrollgremium gemäß Artikel 45d des Grundgesetzes</INS_LANG>
						<MDBINS_VON>24.03.2022</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG>Ordentliches Mitglied</FKT_LANG>
						<FKTINS_VON>24.03.2022</FKTINS_VON>
						<FKTINS_BIS/>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Unterausschuss</INSART_LANG>
						<INS_LANG>UA Abrüstung, Rüstungskontrolle und Nichtverbreitung</INS_LANG>
						<MDBINS_VON>07.04.2022</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG>Obmann</FKT_LANG>
						<FKTINS_VON>07.04.2022</FKTINS_VON>
						<FKTINS_BIS/>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Unterausschuss</INSART_LANG>
						<INS_LANG>UA Abrüstung, Rüstungskontrolle und Nichtverbreitung</INS_LANG>
						<MDBINS_VON>07.04.2022</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG>Ordentliches Mitglied</FKT_LANG>
						<FKTINS_VON>07.04.2022</FKTINS_VON>
						<FKTINS_BIS/>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Untersuchungsausschuss</INSART_LANG>
						<INS_LANG>1. Untersuchungsausschuss</INS_LANG>
						<MDBINS_VON>08.07.2022</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG>Ordentliches Mitglied</FKT_LANG>
						<FKTINS_VON>08.07.2022</FKTINS_VON>
						<FKTINS_BIS/>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Untersuchungsausschuss</INSART_LANG>
						<INS_LANG>1. Untersuchungsausschuss</INS_LANG>
						<MDBINS_VON>08.07.2022</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG>Vorsitzender</FKT_LANG>
						<FKTINS_VON>08.07.2022</FKTINS_VON>
						<FKTINS_BIS/>
					</INSTITUTION>
					<INSTITUTION>
						<INSART_LANG>Ausschuss</INSART_LANG>
						<INS_LANG>Ausschuss für Inneres und Heimat</INS_LANG>
						<MDBINS_VON>19.03.2024</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG>Stellvertretendes Mitglied</FKT_LANG>
						<FKTINS_VON>19.03.2024</FKTINS_VON>
						<FKTINS_BIS/>
					</INSTITUTION>
				</INSTITUTIONEN>
			</WAHLPERIODE>
		</WAHLPERIODEN>
	</MDB>"""
xml = Et.fromstring(xml_string)
test_cases.append(CaseDataforTest((xml), expected=10, exception=None))

xml_string = """<MDB>
		<ID>11000237</ID>
		<NAMEN>
			<NAME>
				<NACHNAME>Bothmer</NACHNAME>
				<VORNAME>Lenelotte</VORNAME>
				<ORTSZUSATZ/>
				<ADEL/>
				<PRAEFIX>von</PRAEFIX>
				<ANREDE_TITEL/>
				<AKAD_TITEL/>
				<HISTORIE_VON>20.10.1969</HISTORIE_VON>
				<HISTORIE_BIS/>
			</NAME>
		</NAMEN>
		<BIOGRAFISCHE_ANGABEN>
			<GEBURTSDATUM>27.10.1915</GEBURTSDATUM>
			<GEBURTSORT>Bremen</GEBURTSORT>
			<GEBURTSLAND/>
			<STERBEDATUM>19.06.1997</STERBEDATUM>
			<GESCHLECHT>weiblich</GESCHLECHT>
			<FAMILIENSTAND>verheiratet, 6 Kinder</FAMILIENSTAND>
			<RELIGION>ohne Angaben</RELIGION>
			<BERUF>Fachschullehrerin</BERUF>
			<PARTEI_KURZ>SPD</PARTEI_KURZ>
			<VITA_KURZ/>
			<VEROEFFENTLICHUNGSPFLICHTIGES/>
		</BIOGRAFISCHE_ANGABEN>
		<WAHLPERIODEN>
			<WAHLPERIODE>
				<WP>6</WP>
				<MDBWP_VON>20.10.1969</MDBWP_VON>
				<MDBWP_BIS>22.09.1972</MDBWP_BIS>
				<WKR_NUMMER/>
				<WKR_NAME/>
				<WKR_LAND/>
				<LISTE>NDS</LISTE>
				<MANDATSART>Landesliste</MANDATSART>
				<INSTITUTIONEN>
					<INSTITUTION>
						<INSART_LANG>Fraktion/Gruppe</INSART_LANG>
						<INS_LANG>Fraktion der Sozialdemokratischen Partei Deutschlands</INS_LANG>
						<MDBINS_VON/>
						<MDBINS_BIS/>
						<FKT_LANG/>
						<FKTINS_VON/>
						<FKTINS_BIS/>
					</INSTITUTION>
				</INSTITUTIONEN>
			</WAHLPERIODE>
			<WAHLPERIODE>
				<WP>7</WP>
				<MDBWP_VON>13.12.1972</MDBWP_VON>
				<MDBWP_BIS>13.12.1976</MDBWP_BIS>
				<WKR_NUMMER/>
				<WKR_NAME/>
				<WKR_LAND/>
				<LISTE>NDS</LISTE>
				<MANDATSART>Landesliste</MANDATSART>
				<INSTITUTIONEN>
					<INSTITUTION>
						<INSART_LANG>Fraktion/Gruppe</INSART_LANG>
						<INS_LANG>Fraktion der Sozialdemokratischen Partei Deutschlands</INS_LANG>
						<MDBINS_VON/>
						<MDBINS_BIS/>
						<FKT_LANG/>
						<FKTINS_VON/>
						<FKTINS_BIS/>
					</INSTITUTION>
				</INSTITUTIONEN>
			</WAHLPERIODE>
			<WAHLPERIODE>
				<WP>8</WP>
				<MDBWP_VON>14.12.1976</MDBWP_VON>
				<MDBWP_BIS>04.11.1980</MDBWP_BIS>
				<WKR_NUMMER/>
				<WKR_NAME/>
				<WKR_LAND/>
				<LISTE>NDS</LISTE>
				<MANDATSART>Landesliste</MANDATSART>
				<INSTITUTIONEN>
					<INSTITUTION>
						<INSART_LANG>Fraktion/Gruppe</INSART_LANG>
						<INS_LANG>Fraktion der Sozialdemokratischen Partei Deutschlands</INS_LANG>
						<MDBINS_VON>14.12.1976</MDBINS_VON>
						<MDBINS_BIS>04.11.1980</MDBINS_BIS>
						<FKT_LANG/>
						<FKTINS_VON/>
						<FKTINS_BIS/>
					</INSTITUTION>
				</INSTITUTIONEN>
			</WAHLPERIODE>
		</WAHLPERIODEN>
	</MDB>"""
xml = Et.fromstring(xml_string)
test_cases.append(CaseDataforTest((xml), expected=3, exception=None))

xml_string = """<MDB>
		<ID>11003569</ID>
		<NAMEN>
			<NAME>
				<NACHNAME>Köhler</NACHNAME>
				<VORNAME>Kristina</VORNAME>
				<ORTSZUSATZ>(Wiesbaden)</ORTSZUSATZ>
				<ADEL/>
				<PRAEFIX/>
				<ANREDE_TITEL>Dr.</ANREDE_TITEL>
				<AKAD_TITEL>Dr.</AKAD_TITEL>
				<HISTORIE_VON>17.10.2002</HISTORIE_VON>
				<HISTORIE_BIS>15.02.2010</HISTORIE_BIS>
			</NAME>
			<NAME>
				<NACHNAME>Schröder</NACHNAME>
				<VORNAME>Kristina</VORNAME>
				<ORTSZUSATZ>(Wiesbaden)</ORTSZUSATZ>
				<ADEL/>
				<PRAEFIX/>
				<ANREDE_TITEL>Dr.</ANREDE_TITEL>
				<AKAD_TITEL>Dr.</AKAD_TITEL>
				<HISTORIE_VON>15.02.2010</HISTORIE_VON>
				<HISTORIE_BIS/>
			</NAME>
		</NAMEN>
		<BIOGRAFISCHE_ANGABEN>
			<GEBURTSDATUM>03.08.1977</GEBURTSDATUM>
			<GEBURTSORT>Wiesbaden</GEBURTSORT>
			<GEBURTSLAND/>
			<STERBEDATUM/>
			<GESCHLECHT>weiblich</GESCHLECHT>
			<FAMILIENSTAND>verheiratet, 2 Kinder</FAMILIENSTAND>
			<RELIGION>evangelisch-lutherisch</RELIGION>
			<BERUF>Dipl.-Soziologin, Bundesministerin a. D.</BERUF>
			<PARTEI_KURZ>CDU</PARTEI_KURZ>
			<VITA_KURZ/>
			<VEROEFFENTLICHUNGSPFLICHTIGES/>
		</BIOGRAFISCHE_ANGABEN>
		<WAHLPERIODEN>
			<WAHLPERIODE>
				<WP>15</WP>
				<MDBWP_VON>17.10.2002</MDBWP_VON>
				<MDBWP_BIS>18.10.2005</MDBWP_BIS>
				<WKR_NUMMER/>
				<WKR_NAME/>
				<WKR_LAND/>
				<LISTE>HES</LISTE>
				<MANDATSART>Landesliste</MANDATSART>
				<INSTITUTIONEN>
					<INSTITUTION>
						<INSART_LANG>Fraktion/Gruppe</INSART_LANG>
						<INS_LANG>Fraktion der Christlich Demokratischen Union/Christlich - Sozialen Union</INS_LANG>
						<MDBINS_VON>17.10.2002</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG/>
						<FKTINS_VON/>
						<FKTINS_BIS/>
					</INSTITUTION>
				</INSTITUTIONEN>
			</WAHLPERIODE>
			<WAHLPERIODE>
				<WP>16</WP>
				<MDBWP_VON>18.10.2005</MDBWP_VON>
				<MDBWP_BIS>27.10.2009</MDBWP_BIS>
				<WKR_NUMMER/>
				<WKR_NAME/>
				<WKR_LAND/>
				<LISTE>HES</LISTE>
				<MANDATSART>Landesliste</MANDATSART>
				<INSTITUTIONEN>
					<INSTITUTION>
						<INSART_LANG>Fraktion/Gruppe</INSART_LANG>
						<INS_LANG>Fraktion der Christlich Demokratischen Union/Christlich - Sozialen Union</INS_LANG>
						<MDBINS_VON>18.10.2005</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG/>
						<FKTINS_VON/>
						<FKTINS_BIS/>
					</INSTITUTION>
				</INSTITUTIONEN>
			</WAHLPERIODE>
			<WAHLPERIODE>
				<WP>17</WP>
				<MDBWP_VON>27.10.2009</MDBWP_VON>
				<MDBWP_BIS>22.10.2013</MDBWP_BIS>   
				<WKR_NUMMER>179</WKR_NUMMER>
				<WKR_NAME>Wiesbaden</WKR_NAME>
				<WKR_LAND>HES</WKR_LAND>
				<LISTE/>
				<MANDATSART>Direktwahl</MANDATSART>
				<INSTITUTIONEN>
					<INSTITUTION>
						<INSART_LANG>Fraktion/Gruppe</INSART_LANG>
						<INS_LANG>Fraktion der Christlich Demokratischen Union/Christlich - Sozialen Union</INS_LANG>
						<MDBINS_VON>27.10.2009</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG/>
						<FKTINS_VON/>
						<FKTINS_BIS/>
					</INSTITUTION>
				</INSTITUTIONEN>
			</WAHLPERIODE>
			<WAHLPERIODE>
				<WP>18</WP>
				<MDBWP_VON>22.10.2013</MDBWP_VON>
				<MDBWP_BIS>24.10.2017</MDBWP_BIS>
				<WKR_NUMMER>179</WKR_NUMMER>
				<WKR_NAME>Wiesbaden</WKR_NAME>
				<WKR_LAND>HE</WKR_LAND>
				<LISTE/>
				<MANDATSART>Direktwahl</MANDATSART>
				<INSTITUTIONEN>
					<INSTITUTION>
						<INSART_LANG>Fraktion/Gruppe</INSART_LANG>
						<INS_LANG>Fraktion der Christlich Demokratischen Union/Christlich - Sozialen Union</INS_LANG>
						<MDBINS_VON>22.10.2013</MDBINS_VON>
						<MDBINS_BIS/>
						<FKT_LANG/>
						<FKTINS_VON/>
						<FKTINS_BIS/>
					</INSTITUTION>
				</INSTITUTIONEN>
			</WAHLPERIODE>
		</WAHLPERIODEN>
	</MDB>"""
xml = Et.fromstring(xml_string)
test_cases.append(CaseDataforTest((xml), expected=8, exception=None))


@pytest.mark.parametrize("case", test_cases)
def test_process_single_mdb(case):
    if case.exception:
        with pytest.raises(case.exception):
            process_single_mdb(case.input)
    else:
        test_result = process_single_mdb(case.input)
        assert case.expected == len(test_result["ui"])
        assert len(test_result) == 15
