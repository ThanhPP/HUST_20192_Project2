package stock

import (
	"net/http"
	"portal/core"
	"portal/dao"
	"portal/model"

	"github.com/labstack/echo"
)

func getAllPredictedPrice(c echo.Context, request interface{}) (statusCode int, data interface{}, lg *model.LogFormat, logResponse bool, err error) {
	ctx := c.Request().Context()
	req := request.(*model.AllRequest)
	lg = &model.LogFormat{Source: c.Request().RemoteAddr, Action: "Get all price"}
	db := core.GetDB()
	sDAO := dao.GetStockDAO()

	res, err := sDAO.GetAllPrice(ctx, db, req.From, req.To)
	if err != nil {
		statusCode, err = http.StatusInternalServerError, err
		return
	}

	return http.StatusOK, res, lg, false, nil
}

func getPredictedPriceByTicket(c echo.Context, request interface{}) (statusCode int, data interface{}, lg *model.LogFormat, logResponse bool, err error) {
	req, ctx := request.(*model.TicketRequest), c.Request().Context()
	lg = &model.LogFormat{Source: c.Request().RemoteAddr, Action: "Get all price"}
	db := core.GetDB()
	sDAO := dao.GetStockDAO()

	res, err := sDAO.GetPriceByTicker(ctx, db, req.Name, req.From, req.To)
	if err != nil {
		statusCode, err = http.StatusInternalServerError, err
		return
	}

	return http.StatusOK, res, lg, false, nil
}

func getPredictedPriceByTickets(c echo.Context, request interface{}) (statusCode int, data interface{}, lg *model.LogFormat, logResponse bool, err error) {
	req, ctx := request.(*model.ManyTicketsRequest), c.Request().Context()
	lg = &model.LogFormat{Source: c.Request().RemoteAddr, Action: "Get all price"}
	db := core.GetDB()
	sDAO := dao.GetStockDAO()

	var resp [][]*model.StockPredicted
	for i := 0; i < len(req.Names); i++ {
		res, err := sDAO.GetPriceByTicker(ctx, db, req.Names[i], req.From, req.To)
		if err != nil {
			statusCode, err = http.StatusInternalServerError, err
			break
		}
		resp = append(resp, res)
	}

	return statusCode, resp, lg, false, err
}
