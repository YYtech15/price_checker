CREATE TABLE IF NOT EXISTS `user` (
	`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`name` TINYTEXT NOT NULL DEFAULT curdate() COLLATE 'utf8mb4_general_ci',
	`pass` TINYTEXT NOT NULL COLLATE 'utf8mb4_general_ci',
	`address` TINYTEXT NOT NULL COLLATE 'utf8mb4_general_ci',
	`created_dt` DATETIME NOT NULL DEFAULT current_timestamp(),
	`update_dt` DATETIME NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
	PRIMARY KEY (`id`) USING BTREE,
	UNIQUE INDEX `address` (`address`) USING HASH
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;
CREATE TABLE `token` (
	`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`token` TINYTEXT NOT NULL COLLATE 'utf8mb4_general_ci',
	`user_id` INT(10) UNSIGNED NOT NULL,
	`created_time` DATETIME NOT NULL DEFAULT current_timestamp(),
	PRIMARY KEY (`id`) USING BTREE,
	UNIQUE INDEX `token` (`token`) USING HASH,
	INDEX `FK_token_user` (`user_id`) USING BTREE,
	CONSTRAINT `FK_token_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;
