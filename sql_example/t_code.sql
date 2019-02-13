ALTER TABLE "table2" DROP CONSTRAINT "fk_table2_table1_1";
ALTER TABLE "table3" DROP CONSTRAINT "m2m_fk_table3_table2_1";

DROP TABLE "table1";
DROP TABLE "table2";
DROP TABLE "table3";

CREATE TABLE "table1" (
"id" int4 NOT NULL,
"test_field" varchar(255) NOT NULL DEFAULT 默认值1,
"test_field2" float8 DEFAULT 2.09,
PRIMARY KEY ("id")
)
WITHOUT OIDS;
COMMENT ON COLUMN "table1"."test_field" IS '测试字段';
COMMENT ON COLUMN "table1"."test_field2" IS '测试字段2';

CREATE TABLE "table2" (
"id" int4 NOT NULL,
"relation_table1" int,
"table3_ids" int,
PRIMARY KEY ("id")
)
WITHOUT OIDS;
COMMENT ON TABLE "table2" IS '表名2';
COMMENT ON COLUMN "table2"."relation_table1" IS '外键字段1';

CREATE TABLE "table3" (
"id" int4 NOT NULL,
"table2_ids" int,
PRIMARY KEY ("id")
)
WITHOUT OIDS;
COMMENT ON COLUMN "table3"."table2_ids" IS '表2关联';


ALTER TABLE "table2" ADD CONSTRAINT "fk_table2_table1_1" FOREIGN KEY ("relation_table1") REFERENCES "table1" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
COMMENT ON CONSTRAINT "fk_table2_table1_1" ON "table2" IS 'm2m';
ALTER TABLE "table3" ADD CONSTRAINT "m2m_fk_table3_table2_1" FOREIGN KEY ("table2_ids") REFERENCES "table2" ("table3_ids") ON DELETE SET NULL;

