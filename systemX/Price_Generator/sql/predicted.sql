CREATE TABLE `predicted` (
    `ticker` char(4) not null primary key,
    `predicted_price` text not null,
    `mse` text not null,
    `mae` text not null,
    `accuracy` text not null);