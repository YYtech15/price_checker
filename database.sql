CREATE TABLE `user` (
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
CREATE TABLE `registerd_items` (
	`user_id` INT(11) UNSIGNED NOT NULL,
	`item_code` TINYTEXT NOT NULL COLLATE 'utf8mb4_general_ci',
	UNIQUE INDEX `user_id_item_code` (`user_id`, `item_code`) USING HASH,
	INDEX `FK__user` (`user_id`) USING BTREE,
	CONSTRAINT `FK__user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;
CREATE TABLE `item_information` (
	`item_code` VARCHAR(13) NOT NULL COLLATE 'utf8mb4_general_ci',
	`name` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`price` INT(11) NULL DEFAULT NULL,
	`url` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`image` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`seller` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`shipping` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	PRIMARY KEY (`item_code`) USING BTREE
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;
CREATE TABLE `message_token` (
	`user_id` INT(10) UNSIGNED NOT NULL,
	`device_token` TINYTEXT NOT NULL COLLATE 'utf8mb4_general_ci',
	UNIQUE INDEX `device_token` (`device_token`) USING HASH,
	INDEX `FK__user2` (`user_id`) USING BTREE,
	CONSTRAINT `FK__user2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;
