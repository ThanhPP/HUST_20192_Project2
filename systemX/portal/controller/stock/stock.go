package stock

import (
	"portal/controller"
	"portal/model"

	"github.com/labstack/echo"
)

func GetAllPredictedPrice(c echo.Context) error {
	return controller.ExecHandler(c, &model.AllRequest{}, getAllPredictedPrice)
}

func GetPredictedPriceByTicket(c echo.Context) error {
	return controller.ExecHandler(c, &model.TicketRequest{}, getPredictedPriceByTicket)
}

func GetPredictedPriceByTickets(c echo.Context) error {
	return controller.ExecHandler(c, &model.ManyTicketsRequest{}, getPredictedPriceByTickets)
}
