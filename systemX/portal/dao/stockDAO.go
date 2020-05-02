package dao

import (
	"context"
	"database/sql"
	"portal/core"
	"portal/model"
)

const (
	GetAllPriceQuery      = "select *from ticker"
	GetPriceByTickerQuery = "select *from ticker where name = ?"
)

type IstockDAO interface {
	GetAllPrice(ctx context.Context, db *sql.DB, start, end string) (priceList []*model.StockPredicted, err error)
	GetPriceByTicker(ctx context.Context, db *sql.DB, ticker, start, end string) (price *model.StockPredicted, err error)
	//	GetPriceByTickers(ctx context.Context, db *sql.DB, ticker []string, start, end string) (priceList []*model.StockPredicted, err error)
}

type stockDAO struct{}

func (s *stockDAO) GetAllPrice(ctx context.Context, db *sql.DB, start, end string) (priceList []*model.StockPredicted, err error) {
	if db == nil {
		return nil, core.ErrDBObjNull
	}

	rows, err := db.QueryContext(ctx, GetAllPriceQuery)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	for rows.Next() {
		var tg = &model.StockPredicted{}
		err := rows.Scan(tg.Name, tg.Price, tg.Timestamp)
		if err != nil {
			return nil, err
		}
		priceList = append(priceList, tg)
	}

	err = rows.Err()
	if err != nil {
		return nil, err
	}
	return
}

func (s *stockDAO) GetPriceByTicker(ctx context.Context, db *sql.DB, ticket, start, end string) (price *model.StockPredicted, err error) {
	if db == nil {
		return nil, core.ErrDBObjNull
	}

	row := db.QueryRowContext(ctx, GetPriceByTickerQuery, ticket)
	err = row.Scan(price)
	if err != nil {
		return nil, err
	}
	return
}

var sDAO IstockDAO = &stockDAO{}

func SetStockDAO(v IstockDAO) {
	sDAO = v
}

func GetStockDAO() IstockDAO {
	return sDAO
}
