CREATE TABLE `predicted` (
    `ticker` varchar(20) not null primary key,
    `price` decimal(12,6),
    `timestamp` datetime,
    `mse` text not null,
    `mae` text not null,
    `accuracy` text not null);