/*
 Navicat Premium Data Transfer

 Source Server         : localhost 5432
 Source Server Type    : PostgreSQL
 Source Server Version : 90202
 Source Host           : localhost
 Source Database       : files
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 90202
 File Encoding         : utf-8

 Date: 06/23/2013 08:13:55 AM
*/

-- ----------------------------
--  Table structure for "strings"
-- ----------------------------
DROP TABLE IF EXISTS "strings";
CREATE TABLE "strings" (
	"str_id" varchar(10) NOT NULL,
	"string" varchar(256) NOT NULL,
	"str_ts" tsvector
)
WITH (OIDS=FALSE);
ALTER TABLE "strings" OWNER TO "donb";

-- ----------------------------
--  Records of "strings"
-- ----------------------------
BEGIN;
INSERT INTO "strings" VALUES ('str000005', 'Jaguar God', '''god'':2 ''jaguar'':1');
INSERT INTO "strings" VALUES ('str000006', 'Sunglasses After Dark', '''dark'':3 ''sunglass'':1');
INSERT INTO "strings" VALUES ('str000007', 'Warehouse 13', '''13'':2 ''warehous'':1');
INSERT INTO "strings" VALUES ('str000008', 'Warehouse 13 cbr', '''13'':2 ''cbr'':3 ''warehous'':1');
INSERT INTO "strings" VALUES ('str000009', '60 Minutes', '''60'':1 ''minut'':2');
INSERT INTO "strings" VALUES ('str000010', 'TV Show', '''show'':2 ''tv'':1');
INSERT INTO "strings" VALUES ('str000011', 'TV Show—single', '''show'':2 ''singl'':3 ''tv'':1');
INSERT INTO "strings" VALUES ('str000012', 'Comic', '''comic'':1');
INSERT INTO "strings" VALUES ('str000013', 'Walt Disney World', '''disney'':2 ''walt'':1 ''world'':3');
INSERT INTO "strings" VALUES ('str000014', 'location', '''locat'':1');
INSERT INTO "strings" VALUES ('str000015', 'Fathom', '''fathom'':1');
INSERT INTO "strings" VALUES ('str000016', 'comic', '''comic'':1');
INSERT INTO "strings" VALUES ('str000017', 'Soulfire', '''soulfir'':1');
INSERT INTO "strings" VALUES ('str000018', 'Urban guerrilla', '''guerrilla'':2 ''urban'':1');
INSERT INTO "strings" VALUES ('str000019', 'character type', '''charact'':1 ''type'':2');
INSERT INTO "strings" VALUES ('str000020', 'Virtual Reality', '''realiti'':2 ''virtual'':1');
INSERT INTO "strings" VALUES ('str000021', 'simulation', '''simul'':1');
INSERT INTO "strings" VALUES ('str000022', 'Starlex', '''starlex'':1');
INSERT INTO "strings" VALUES ('str000023', 'Comic Book Women', '''book'':2 ''comic'':1 ''women'':3');
INSERT INTO "strings" VALUES ('str000024', 'character reference', '''charact'':1 ''refer'':2');
INSERT INTO "strings" VALUES ('str000025', 'AYURVEDA', '''ayurveda'':1');
INSERT INTO "strings" VALUES ('str000026', 'ancient system', '''ancient'':1 ''system'':2');
INSERT INTO "strings" VALUES ('str000027', 'Executive Assistant', '''assist'':2 ''execut'':1');
INSERT INTO "strings" VALUES ('str000028', 'LUXOLOGY_MODO', '''luxolog'':1 ''modo'':2');
INSERT INTO "strings" VALUES ('str000029', 'application (notes)', '''applic'':1 ''note'':2');
INSERT INTO "strings" VALUES ('str000030', 'Playboy Plus FullHD', '''fullhd'':3 ''playboy'':1 ''plus'':2');
INSERT INTO "strings" VALUES ('str000031', 'character anim ref (hires)', '''anim'':2 ''charact'':1 ''hire'':4 ''ref'':3');
INSERT INTO "strings" VALUES ('str000032', 'Miss Fury', '''furi'':2 ''miss'':1');
INSERT INTO "strings" VALUES ('str000033', 'Saga', '''saga'':1');
INSERT INTO "strings" VALUES ('str000034', 'C', '''c'':1');
INSERT INTO "strings" VALUES ('str000035', 'programming language', '''languag'':2 ''program'':1');
INSERT INTO "strings" VALUES ('str000036', 'Infinite Horizon', '''horizon'':2 ''infinit'':1');
INSERT INTO "strings" VALUES ('str000037', 'Danger Girl', '''danger'':1 ''girl'':2');
INSERT INTO "strings" VALUES ('str000038', 'comic book girl', '''book'':2 ''comic'':1 ''girl'':3');
INSERT INTO "strings" VALUES ('str000039', 'Terence McKenna', '''mckenna'':2 ''terenc'':1');
INSERT INTO "strings" VALUES ('str000040', 'author', '''author'':1');
INSERT INTO "strings" VALUES ('str000041', 'Your Brain', '''brain'':2');
INSERT INTO "strings" VALUES ('str000042', 'area of study', '''area'':1 ''studi'':3');
INSERT INTO "strings" VALUES ('str000043', 'Witchblade', '''witchblad'':1');
INSERT INTO "strings" VALUES ('str000044', 'Amy Adams', '''adam'':2 ''ami'':1');
INSERT INTO "strings" VALUES ('str000045', 'actress', '''actress'':1');
INSERT INTO "strings" VALUES ('str000046', 'User Interface Design', '''design'':3 ''interfac'':2 ''user'':1');
INSERT INTO "strings" VALUES ('str000047', 'design area', '''area'':2 ''design'':1');
INSERT INTO "strings" VALUES ('str000048', 'plastics', '''plastic'':1');
INSERT INTO "strings" VALUES ('str000049', '<supername>', '');
INSERT INTO "strings" VALUES ('str000050', 'Paramahansa Yogananda', '''paramahansa'':1 ''yogananda'':2');
INSERT INTO "strings" VALUES ('str000051', 'Natural Eyesight Improvement', '''eyesight'':2 ''improv'':3 ''natur'':1');
INSERT INTO "strings" VALUES ('str000052', 'Jean Baudrillard', '''baudrillard'':2 ''jean'':1');
INSERT INTO "strings" VALUES ('str000053', 'Code Lyoko', '''code'':1 ''lyoko'':2');
INSERT INTO "strings" VALUES ('str000054', 'TV show', '''show'':2 ''tv'':1');
INSERT INTO "strings" VALUES ('str000055', 'Max Steel', '''max'':1 ''steel'':2');
INSERT INTO "strings" VALUES ('str000056', 'Shatter', '''shatter'':1');
INSERT INTO "strings" VALUES ('str000057', 'SQL and Relational Theory', '''relat'':3 ''sql'':1 ''theori'':4');
INSERT INTO "strings" VALUES ('str000058', 'programming', '''program'':1');
INSERT INTO "strings" VALUES ('str000059', 'East of West', '''east'':1 ''west'':3');
INSERT INTO "strings" VALUES ('str000060', 'Nude', '''nude'':1');
INSERT INTO "strings" VALUES ('str000061', 'Stephen R. Covey', '''covey'':3 ''r'':2 ''stephen'':1');
INSERT INTO "strings" VALUES ('str000062', 'JavaScript', '''javascript'':1');
INSERT INTO "strings" VALUES ('str000063', 'Enterprise Games', '''enterpris'':1 ''game'':2');
INSERT INTO "strings" VALUES ('str000064', 'game design', '''design'':2 ''game'':1');
INSERT INTO "strings" VALUES ('str000065', 'William James', '''jame'':2 ''william'':1');
INSERT INTO "strings" VALUES ('str000066', 'ethernet switches', '''ethernet'':1 ''switch'':2');
INSERT INTO "strings" VALUES ('str000067', 'network design', '''design'':2 ''network'':1');
INSERT INTO "strings" VALUES ('str000068', 'Hackers', '''hacker'':1');
INSERT INTO "strings" VALUES ('str000069', 'Aperture', '''apertur'':1');
INSERT INTO "strings" VALUES ('str000070', 'book', '''book'':1');
INSERT INTO "strings" VALUES ('str000071', 'cookbook', '''cookbook'':1');
INSERT INTO "strings" VALUES ('str000072', 'Teen Titans Go', '''go'':3 ''teen'':1 ''titan'':2');
INSERT INTO "strings" VALUES ('str000073', 'animated tv series', '''anim'':1 ''seri'':3 ''tv'':2');
INSERT INTO "strings" VALUES ('str000074', 'D3', '''d3'':1');
INSERT INTO "strings" VALUES ('str000075', 'JavaScript library', '''javascript'':1 ''librari'':2');
INSERT INTO "strings" VALUES ('str000076', 'Big Data', '''big'':1 ''data'':2');
INSERT INTO "strings" VALUES ('str000077', 'Fuzzy Sets', '''fuzzi'':1 ''set'':2');
INSERT INTO "strings" VALUES ('str000078', 'mathematics', '''mathemat'':1');
INSERT INTO "strings" VALUES ('str000079', 'FLCL', '''flcl'':1');
INSERT INTO "strings" VALUES ('str000080', 'anime', '''anim'':1');
INSERT INTO "strings" VALUES ('str000081', 'ZeroMQ', '''zeromq'':1');
INSERT INTO "strings" VALUES ('str000082', 'networking library', '''librari'':2 ''network'':1');
INSERT INTO "strings" VALUES ('str000083', 'VMware', '''vmware'':1');
INSERT INTO "strings" VALUES ('str000084', 'nonviolence', '''nonviol'':1');
INSERT INTO "strings" VALUES ('str000085', 'etiquette', '''etiquett'':1');
INSERT INTO "strings" VALUES ('str000086', 'coffee', '''coffe'':1');
INSERT INTO "strings" VALUES ('str000087', 'Birds of Prey', '''bird'':1 ''prey'':3');
INSERT INTO "strings" VALUES ('str000088', 'fashion', '''fashion'':1');
INSERT INTO "strings" VALUES ('str000089', 'Organizing', '''organ'':1');
INSERT INTO "strings" VALUES ('str000090', 'Joyce Carol Oates', '''carol'':2 ''joyc'':1 ''oat'':3');
INSERT INTO "strings" VALUES ('str000091', 'NumPy', '''numpi'':1');
INSERT INTO "strings" VALUES ('str000092', 'python', '''python'':1');
INSERT INTO "strings" VALUES ('str000093', 'Ganglia', '''ganglia'':1');
INSERT INTO "strings" VALUES ('str000094', 'distributed monitoring system', '''distribut'':1 ''monitor'':2 ''system'':3');
INSERT INTO "strings" VALUES ('str000095', 'instrumentation', '''instrument'':1');
INSERT INTO "strings" VALUES ('str000096', 'The Art of Community', '''art'':2 ''communiti'':4');
INSERT INTO "strings" VALUES ('str000097', 'Nebula Awards', '''award'':2 ''nebula'':1');
INSERT INTO "strings" VALUES ('str000098', 'sci-fi', '''fi'':3 ''sci'':2 ''sci-fi'':1');
INSERT INTO "strings" VALUES ('str000099', 'XXX', '''xxx'':1');
INSERT INTO "strings" VALUES ('str000100', 'Catwoman', '''catwoman'':1');
INSERT INTO "strings" VALUES ('str000101', 'SFX', '''sfx'':1');
INSERT INTO "strings" VALUES ('str000102', 'Magazine', '''magazin'':1');
INSERT INTO "strings" VALUES ('str000103', 'Code', '''code'':1');
INSERT INTO "strings" VALUES ('str000104', 'Computer Vision', '''comput'':1 ''vision'':2');
INSERT INTO "strings" VALUES ('str000105', 'Heroku', '''heroku'':1');
INSERT INTO "strings" VALUES ('str000106', 'house maintainence', '''hous'':1 ''maintain'':2');
INSERT INTO "strings" VALUES ('str000107', 'Taylor Swift', '''swift'':2 ''taylor'':1');
INSERT INTO "strings" VALUES ('str000108', 'singer', '''singer'':1');
INSERT INTO "strings" VALUES ('str000109', 'WIRED', '''wire'':1');
INSERT INTO "strings" VALUES ('str000110', 'magazine', '''magazin'':1');
INSERT INTO "strings" VALUES ('str000111', 'Networks-on-Chips', '''chip'':4 ''network'':2 ''networks-on-chip'':1');
INSERT INTO "strings" VALUES ('str000112', 'Virtualization', '''virtual'':1');
INSERT INTO "strings" VALUES ('str000113', 'Borges, Jorge Luis', '''borg'':1 ''jorg'':2 ''lui'':3');
INSERT INTO "strings" VALUES ('str000114', 'Tom Robbins', '''robbin'':2 ''tom'':1');
INSERT INTO "strings" VALUES ('str000115', 'Edge', '''edg'':1');
INSERT INTO "strings" VALUES ('str000116', 'history of science', '''histori'':1 ''scienc'':3');
INSERT INTO "strings" VALUES ('str000117', 'Science—Popular works', '''popular'':2 ''scienc'':1 ''work'':3');
INSERT INTO "strings" VALUES ('str000118', 'science', '''scienc'':1');
INSERT INTO "strings" VALUES ('str000119', 'Science of Politics', '''polit'':3 ''scienc'':1');
INSERT INTO "strings" VALUES ('str000120', 'Hacking', '''hack'':1');
INSERT INTO "strings" VALUES ('str000121', 'Popular Mechanics', '''mechan'':2 ''popular'':1');
INSERT INTO "strings" VALUES ('str000122', 'Flight', '''flight'':1');
INSERT INTO "strings" VALUES ('str000123', 'aerodynamics', '''aerodynam'':1');
INSERT INTO "strings" VALUES ('str000124', 'Computer Organization', '''comput'':1 ''organ'':2');
INSERT INTO "strings" VALUES ('str000125', 'Phil Jackson', '''jackson'':2 ''phil'':1');
INSERT INTO "strings" VALUES ('str000126', 'Arduino', '''arduino'':1');
INSERT INTO "strings" VALUES ('str000127', 'hardware', '''hardwar'':1');
INSERT INTO "strings" VALUES ('str000128', 'neuro', '''neuro'':1');
INSERT INTO "strings" VALUES ('str000129', 'Dan Brown', '''brown'':2 ''dan'':1');
INSERT INTO "strings" VALUES ('str000130', 'Node Applications', '''applic'':2 ''node'':1');
INSERT INTO "strings" VALUES ('str000131', 'Scott Adams', '''adam'':2 ''scott'':1');
INSERT INTO "strings" VALUES ('str000132', 'Asimovs Science Fiction', '''asimov'':1 ''fiction'':3 ''scienc'':2');
INSERT INTO "strings" VALUES ('str000133', 'sci-fi magazine', '''fi'':3 ''magazin'':4 ''sci'':2 ''sci-fi'':1');
INSERT INTO "strings" VALUES ('str000134', 'Locus', '''locus'':1');
INSERT INTO "strings" VALUES ('str000135', 'DAZ Studio', '''daz'':1 ''studio'':2');
INSERT INTO "strings" VALUES ('str000136', 'Ray Kurzweil', '''kurzweil'':2 ''ray'':1');
INSERT INTO "strings" VALUES ('str000137', 'Rachel Weisz', '''rachel'':1 ''weisz'':2');
INSERT INTO "strings" VALUES ('str000138', 'Steven Levy', '''levi'':2 ''steven'':1');
INSERT INTO "strings" VALUES ('str000139', 'Money', '''money'':1');
INSERT INTO "strings" VALUES ('str000140', 'Nginx', '''nginx'':1');
INSERT INTO "strings" VALUES ('str000141', 'Nginx Web Server', '''nginx'':1 ''server'':3 ''web'':2');
INSERT INTO "strings" VALUES ('str000142', 'Character Animation', '''anim'':2 ''charact'':1');
INSERT INTO "strings" VALUES ('str000143', 'technique', '''techniqu'':1');
INSERT INTO "strings" VALUES ('str000144', 'Joanna Russ', '''joanna'':1 ''russ'':2');
INSERT INTO "strings" VALUES ('str000145', 'Neal Stephenson', '''neal'':1 ''stephenson'':2');
INSERT INTO "strings" VALUES ('str000146', 'Douglas Hofstadter', '''dougla'':1 ''hofstadt'':2');
INSERT INTO "strings" VALUES ('str000147', 'The Grove Nymph', '''grove'':2 ''nymph'':3');
INSERT INTO "strings" VALUES ('str000148', 'Wonder Woman', '''woman'':2 ''wonder'':1');
INSERT INTO "strings" VALUES ('str000149', 'UI design', '''design'':2 ''ui'':1');
INSERT INTO "strings" VALUES ('str000150', 'Bertrand Russell', '''bertrand'':1 ''russel'':2');
INSERT INTO "strings" VALUES ('str000151', 'Storytelling', '''storytel'':1');
INSERT INTO "strings" VALUES ('str000152', 'Artificial Brains', '''artifici'':1 ''brain'':2');
INSERT INTO "strings" VALUES ('str000153', 'Brain Machine Interface', '''brain'':1 ''interfac'':3 ''machin'':2');
INSERT INTO "strings" VALUES ('str000154', 'Cognitive Neurosci', '''cognit'':1 ''neurosci'':2');
INSERT INTO "strings" VALUES ('str000155', 'Mac OS X—Internals', '''intern'':4 ''mac'':1 ''os'':2 ''x'':3');
INSERT INTO "strings" VALUES ('str000156', 'Zombie', '''zombi'':1');
INSERT INTO "strings" VALUES ('str000157', 'Proof Theory - The First Step into Impredicativity - W. Pohlers (Springer, 2009) WW.pdf', '''2009'':11 ''first'':4 ''impred'':7 ''pohler'':9 ''proof'':1 ''springer'':10 ''step'':5 ''theori'':2 ''w'':8 ''ww.pdf'':12');
INSERT INTO "strings" VALUES ('str000158', 'math', '''math'':1');
INSERT INTO "strings" VALUES ('str000159', 'The Man From UNCLE', '''man'':2 ''uncl'':4');
INSERT INTO "strings" VALUES ('str000160', 'Gamecca', '''gamecca'':1');
INSERT INTO "strings" VALUES ('str000161', 'game magazine', '''game'':1 ''magazin'':2');
INSERT INTO "strings" VALUES ('str000162', 'Cinema', '''cinema'':1');
INSERT INTO "strings" VALUES ('str000163', 'Fiction', '''fiction'':1');
INSERT INTO "strings" VALUES ('str000164', 'art', '''art'':1');
INSERT INTO "strings" VALUES ('str000165', 'Final Cut Pro', '''cut'':2 ''final'':1 ''pro'':3');
INSERT INTO "strings" VALUES ('str000166', 'MapReduce', '''mapreduc'':1');
INSERT INTO "strings" VALUES ('str000167', 'Dirac', '''dirac'':1');
INSERT INTO "strings" VALUES ('str000168', 'physicist', '''physicist'':1');
INSERT INTO "strings" VALUES ('str000169', 'Michael Crichton', '''crichton'':2 ''michael'':1');
INSERT INTO "strings" VALUES ('str000170', 'Supergirl', '''supergirl'':1');
INSERT INTO "strings" VALUES ('str000171', 'epub', '''epub'':1');
INSERT INTO "strings" VALUES ('str000172', 'Wireshark', '''wireshark'':1');
INSERT INTO "strings" VALUES ('str000173', 'networking', '''network'':1');
INSERT INTO "strings" VALUES ('str000174', 'Programmer', '''programm'':1');
INSERT INTO "strings" VALUES ('str000175', 'mobi', '''mobi'':1');
INSERT INTO "strings" VALUES ('str000176', 'Pink Floyd', '''floyd'':2 ''pink'':1');
INSERT INTO "strings" VALUES ('str000177', 'Cinematographer', '''cinematograph'':1');
INSERT INTO "strings" VALUES ('str000178', 'film', '''film'':1');
INSERT INTO "strings" VALUES ('str000179', 'Dalai Lama', '''dalai'':1 ''lama'':2');
INSERT INTO "strings" VALUES ('str000180', 'Green Lantern Corps', '''corp'':3 ''green'':1 ''lantern'':2');
INSERT INTO "strings" VALUES ('str000181', 'Katana', '''katana'':1');
INSERT INTO "strings" VALUES ('str000182', 'Buffy the Vampire Slayer Season 9', '''9'':6 ''buffi'':1 ''season'':5 ''slayer'':4 ''vampir'':3');
INSERT INTO "strings" VALUES ('str000183', 'cbr', '''cbr'':1');
INSERT INTO "strings" VALUES ('str000184', 'Crisis on Infinite Earths', '''crisi'':1 ''earth'':4 ''infinit'':3');
INSERT INTO "strings" VALUES ('str000185', 'Writing', '''write'':1');
INSERT INTO "strings" VALUES ('str000186', 'Los Alamos From Below', '''alamo'':2 ''los'':1');
INSERT INTO "strings" VALUES ('str000187', 'Feynman', '''feynman'':1');
INSERT INTO "strings" VALUES ('str000188', 'Twitter', '''twitter'':1');
INSERT INTO "strings" VALUES ('str000189', 'online service', '''onlin'':1 ''servic'':2');
INSERT INTO "strings" VALUES ('str000190', 'robert parker', '''parker'':2 ''robert'':1');
INSERT INTO "strings" VALUES ('str000191', 'Spenser Series #38', '''38'':3 ''seri'':2 ''spenser'':1');
INSERT INTO "strings" VALUES ('str000192', '3D Artist', '''3d'':1 ''artist'':2');
INSERT INTO "strings" VALUES ('str000193', 'art production magazine', '''art'':1 ''magazin'':3 ''product'':2');
INSERT INTO "strings" VALUES ('str000194', 'Katie Melua', '''kati'':1 ''melua'':2');
INSERT INTO "strings" VALUES ('str000195', 'Hannah Arendt', '''arendt'':2 ''hannah'':1');
INSERT INTO "strings" VALUES ('str000196', 'political theorist', '''polit'':1 ''theorist'':2');
INSERT INTO "strings" VALUES ('str000197', 'cbz', '''cbz'':1');
INSERT INTO "strings" VALUES ('str000198', 'mathematics as intellectual process', '''intellectu'':3 ''mathemat'':1 ''process'':4');
INSERT INTO "strings" VALUES ('str000199', 'Philosophy', '''philosophi'':1');
INSERT INTO "strings" VALUES ('str000200', 'subject', '''subject'':1');
INSERT INTO "strings" VALUES ('str000201', 'Terminator Salvation: The Machinima Series', '''machinima'':4 ''salvat'':2 ''seri'':5 ''termin'':1');
INSERT INTO "strings" VALUES ('str000202', 'machinima series', '''machinima'':1 ''seri'':2');
INSERT INTO "strings" VALUES ('str000203', 'Leary', '''leari'':1');
INSERT INTO "strings" VALUES ('str000204', 'bitcoin', '''bitcoin'':1');
INSERT INTO "strings" VALUES ('str000205', 'digital currency', '''currenc'':2 ''digit'':1');
INSERT INTO "strings" VALUES ('str000206', 'Ayurvedic', '''ayurved'':1');
INSERT INTO "strings" VALUES ('str000207', 'Photographing Nudes', '''nude'':2 ''photograph'':1');
INSERT INTO "strings" VALUES ('str000208', 'Business Success', '''busi'':1 ''success'':2');
INSERT INTO "strings" VALUES ('str000209', 'Privacy', '''privaci'':1');
INSERT INTO "strings" VALUES ('str000210', 'Accounting', '''account'':1');
INSERT INTO "strings" VALUES ('str000211', 'Recasting', '''recast'':1');
INSERT INTO "strings" VALUES ('str000212', 'Sharapova', '''sharapova'':1');
INSERT INTO "strings" VALUES ('str000213', 'athlete', '''athlet'':1');
INSERT INTO "strings" VALUES ('str000214', 'Python', '''python'':1');
INSERT INTO "strings" VALUES ('str000215', 'A Distant Soil', '''distant'':2 ''soil'':3');
INSERT INTO "strings" VALUES ('str000216', 'Harley Quinn', '''harley'':1 ''quinn'':2');
INSERT INTO "strings" VALUES ('str000217', 'Maya', '''maya'':1');
INSERT INTO "strings" VALUES ('str000218', 'art production', '''art'':1 ''product'':2');
INSERT INTO "strings" VALUES ('str000219', 'Rational Mysticism', '''mystic'':2 ''ration'':1');
INSERT INTO "strings" VALUES ('str000220', 'Mass Effect', '''effect'':2 ''mass'':1');
INSERT INTO "strings" VALUES ('str000221', 'videogame', '''videogam'':1');
INSERT INTO "strings" VALUES ('str000222', 'Cyberforce', '''cyberforc'':1');
INSERT INTO "strings" VALUES ('str000223', 'The Reverse Thing', '''revers'':2 ''thing'':3');
INSERT INTO "strings" VALUES ('str000224', 'perception exercise', '''exercis'':2 ''percept'':1');
INSERT INTO "strings" VALUES ('str000225', 'Douglas Coupland', '''coupland'':2 ''dougla'':1');
INSERT INTO "strings" VALUES ('str000226', 'Planetoid cbr', '''cbr'':2 ''planetoid'':1');
INSERT INTO "strings" VALUES ('str000227', 'FEMJOY', '''femjoy'':1');
INSERT INTO "strings" VALUES ('str000228', 'vogue', '''vogu'':1');
INSERT INTO "strings" VALUES ('str000229', 'scientific method', '''method'':2 ''scientif'':1');
INSERT INTO "strings" VALUES ('str000230', 'string theory', '''string'':1 ''theori'':2');
INSERT INTO "strings" VALUES ('str000231', 'Batwoman', '''batwoman'':1');
INSERT INTO "strings" VALUES ('str000232', 'Lesbian', '''lesbian'':1');
INSERT INTO "strings" VALUES ('str000233', 'Evo pdf', '''evo'':1 ''pdf'':2');
INSERT INTO "strings" VALUES ('str000234', 'driving magazine', '''drive'':1 ''magazin'':2');
COMMIT;

-- ----------------------------
--  Primary key structure for table "strings"
-- ----------------------------
ALTER TABLE "strings" ADD CONSTRAINT "names_pkey" PRIMARY KEY ("str_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

