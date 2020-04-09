alter table asset
	add remark longtext null after os;
alter table asset
    add sub_domain longtext null after remark;
alter table asset
	add dns longtext null after sub_domain;
