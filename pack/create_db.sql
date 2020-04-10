create schema if not exists `sec` collate utf8_general_ci;
use `sec`;
create table if not exists `asset`
(
    `id`          bigint auto_increment primary key,
    `ip`          varchar(128) null,
    `tags`        varchar(256) null,
    `region`      varchar(64)  null,
    `ports`       longtext     null,
    `os`          longtext     null,
    `remark`      longtext     null,
    `sub_domain`  longtext     null,
    `dns`         longtext     null,
    `create_time` datetime     null,
    `modify_time` datetime     null
);

create table if not exists `dict`
(
    `id`          bigint auto_increment primary key,
    `dict_key`    varchar(256) null,
    `dict_value`  longtext     null,
    `remark`      varchar(256) null,
    `create_time` datetime     null,
    `modify_time` datetime     null
);

create table if not exists `plugin`
(
    `id`          bigint auto_increment primary key,
    `title`       varchar(256)     null,
    `remark`      longtext         null,
    `publisher`   varchar(128)     null,
    `script`      varchar(256)     null,
    `label`       varchar(64)      null,
    `hide`        int(1) default 0 null,
    `create_time` datetime         null,
    `modify_time` datetime         null
);

create table if not exists `task`
(
    `id`           bigint auto_increment primary key,
    `task_name`    varchar(256) null,
    `script`       varchar(265) null,
    `script_name`  varchar(256) null,
    `target`       varchar(128) null,
    `state`        varchar(65)  null,
    `cron`         varchar(64)  null,
    `result`       longtext     null,
    `result_state` tinyint(1)   null,
    `handle_state` varchar(64)  null,
    `handle_node`  varchar(256) null,
    `create_time`  datetime     null,
    `modify_time`  datetime     null
);

create table if not exists `user`
(
    `id`          bigint auto_increment primary key,
    `user_name`   varchar(64)  null,
    `pass_word`   varchar(128) null,
    `salt`        varchar(128) null,
    `state`       varchar(64)  null,
    `type`        varchar(64)  null,
    `create_time` datetime     null,
    `modify_time` datetime     null
);



alter table sec.asset
    convert to character set utf8;
alter table sec.plugin
    convert to character set utf8;
alter table sec.task
    convert to character set utf8;
ALTER TABLE sec.asset
    DEFAULT CHARACTER SET utf8;
ALTER TABLE sec.plugin
    DEFAULT CHARACTER SET utf8;
ALTER TABLE sec.task
    DEFAULT CHARACTER SET utf8;

DROP PROCEDURE IF EXISTS pro_AddColumn;
DELIMITER //
CREATE PROCEDURE pro_AddColumn()
BEGIN

    IF NOT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name = 'asset' AND COLUMN_NAME = 'remark') THEN
        alter table sec.asset
            add remark longtext null after os;
    END IF;

    IF NOT EXISTS(
            SELECT 1 FROM information_schema.columns WHERE table_name = 'asset' AND COLUMN_NAME = 'sub_domain') THEN
        alter table sec.asset
            add sub_domain longtext null after remark;
    END IF;

    IF NOT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name = 'asset' AND COLUMN_NAME = 'dns') THEN
        alter table sec.asset
            add dns longtext null after sub_domain;
    END IF;

END//
DELIMITER ;
CALL pro_AddColumn;
DROP PROCEDURE pro_AddColumn;