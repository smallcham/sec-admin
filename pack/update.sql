

DROP PROCEDURE IF EXISTS pro_AddColumn;
CREATE PROCEDURE pro_AddColumn() BEGIN

IF NOT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='asset' AND COLUMN_NAME='remark') THEN
alter table sec.asset add remark longtext null after os;
END IF;

IF NOT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='asset' AND COLUMN_NAME='sub_domain') THEN
alter table sec.asset add sub_domain longtext null after remark;
END IF;

IF NOT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='asset' AND COLUMN_NAME='dns') THEN
alter table sec.asset add dns longtext null after sub_domain;
END IF;

END;
CALL pro_AddColumn;
DROP PROCEDURE pro_AddColumn;