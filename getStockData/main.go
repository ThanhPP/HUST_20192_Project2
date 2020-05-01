package main

import (
	"fmt"
	"hash/fnv"
	"sync"

	"database/sql"

	_ "github.com/go-sql-driver/mysql"
	"github.com/markcheno/go-quote"
	"github.com/spf13/viper"
)

type Config struct {
	webServer *webServerConfig
	shard     *shardConfig
	stockList []string
}
type webServerConfig struct {
	Port int
	Cert string
	Key  string
}
type shardConfig struct {
	ShardNumber   int
	ShardAddress  []string
	ShardDBType   []string
	ShardDBName   []string
	ShardUserName []string
	ShardPassword []string
	MaxIdleConn   int
	MaxOpenConn   int
	IsWsrep       bool
}

var config *Config
var dbShardObj []*DBShardObj

func init() {
	viper.SetConfigName("config")
	viper.SetConfigType("toml")
	viper.AddConfigPath(".")

	if err := viper.ReadInConfig(); err != nil {
		panic(err)
	}
	// } else {
	// 	viper.AutomaticEnv()
	// }

	config = &Config{
		webServer: &webServerConfig{
			Port: viper.GetInt("PORT"),
			Cert: viper.GetString("CERT"),
			Key:  viper.GetString("KEY"),
		},
		shard: &shardConfig{
			ShardNumber:   viper.GetInt("SHARD_NUMBER"),
			ShardAddress:  viper.GetStringSlice("SHARD_ADDRESS"),
			ShardDBType:   viper.GetStringSlice("SHARD_TYPE"),
			ShardDBName:   viper.GetStringSlice("SHARD_NAME"),
			ShardUserName: viper.GetStringSlice("SHARD_USER"),
			ShardPassword: viper.GetStringSlice("SHARD_PASSWORD"),
			MaxIdleConn:   viper.GetInt("DB_MAX_IDLE"),
			MaxOpenConn:   viper.GetInt("DB_MAX_OPEN"),
			IsWsrep:       false,
		},
		stockList: viper.GetStringSlice("STOCK_LIST"),
	}

	// init db shard Obj
	dbShardObj = make([]*DBShardObj, config.shard.ShardNumber)

	for i := 0; i < config.shard.ShardNumber; i++ {
		dns := config.shard.ShardUserName[i] + ":" + config.shard.ShardPassword[i] + "@tcp(" + config.shard.ShardAddress[i] + ")/" + config.shard.ShardDBName[i]

		//	db, err := sql.Open("mysql",
		//		"user:password@tcp(127.0.0.1:3306)/hello")
		db, err := sql.Open("mysql", dns)
		if err != nil {
			panic(err)
		}
		dbShardObj[i] = &DBShardObj{db: db, ShardID: uint32(i)}
		//		defer db.Close()
	}
}

type DBShardObj struct {
	db      *sql.DB
	ShardID uint32
	sync.RWMutex
}

func getShardID(stockname string) uint32 {
	return getHash(stockname) % uint32(config.shard.ShardNumber)
}

//getHash hash string to uint32
func getHash(s string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(s))
	return h.Sum32()
}

func writeToDB(shardID uint32, stockData quote.Quote, stockName string) error {
	dbShardObj[shardID].Lock()

	tx, err := dbShardObj[shardID].db.Begin()
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}
	defer tx.Rollback()

	fmt.Println(stockName)

	st := "DROP TABLE IF EXISTS `" + stockName + "`"

	st2 := "CREATE TABLE " + stockName + "(`id` INTEGER PRIMARY KEY auto_increment,`timestamp` DATETIME NOT NULL,`open` DECIMAL(12, 6) NOT NULL,`high` DECIMAL(12, 6) NOT NULL,`low` DECIMAL(12, 6) NOT NULL,`close` DECIMAL(12, 6) NOT NULL,`volume` DECIMAL(18,10) NOT NULL);"

	st3 := "INSERT INTO " + stockName + " (timestamp, open, high, low, close, volume) values (?,?,?,?,?,?);"

	stmtCreate1, err := tx.Prepare(st)
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}

	stmtCreate2, err := tx.Prepare(st2)
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}

	_, err = stmtCreate1.Exec()
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}
	stmtCreate1.Close()

	_, err = stmtCreate2.Exec()
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}
	stmtCreate2.Close()

	stmt, err := tx.Prepare(st3)
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}

	for i := 0; i < len(stockData.Date); i++ {
		_, err = stmt.Exec(stockData.Date[i], stockData.Open[i], stockData.High[i], stockData.Low[i], stockData.Close[i], stockData.Volume[i])
		if err != nil {
			dbShardObj[shardID].Unlock()
			return err
		}

	}

	st4 := "insert into ticker(name,status) values (?,?)"
	/*
		st5 := "update ticker set name status=? where name=?"

		stmtTicker, err := tx.Prepare("select status from ticker where name=?")
		k, err := stmtTicker.Exec(stockName)
		if err != nil {
			dbShardObj[shardID].Unlock()
			return err
		}


		if k != nil {
			stmtTicker2, err := tx.Prepare(st5)
			if err != nil {
				dbShardObj[shardID].Unlock()
				return err
			}

			_, err = stmtTicker2.Exec("ok", stockName)
			if err != nil {
				dbShardObj[shardID].Unlock()
				return err
			}

		} else {
	*/
	stmtTicker2, err := tx.Prepare(st4)
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}

	_, err = stmtTicker2.Exec(stockName, "ok")
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}

	//}

	err = tx.Commit()
	if err != nil {
		dbShardObj[shardID].Unlock()
		return err
	}

	dbShardObj[shardID].Unlock()
	return err
}

func getDataFromYahoo(stockName string) error {

	stockData, err := quote.NewQuoteFromYahoo(stockName, "2010-01-01", "2020-04-01", quote.Daily, true)
	if err != nil {
		return err
	}
	hash := getHash(stockName)
	err = writeToDB(hash%uint32(config.shard.ShardNumber), stockData, stockName)
	return err
}

func main() {
	for i := 0; i < len(config.stockList); i++ {
		err := getDataFromYahoo(config.stockList[i])
		if err != nil {
			fmt.Println(err)
		}
	}
}
