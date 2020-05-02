package webserver

import (
	"context"
	"crypto/tls"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"sync"

	"portal/controller/stock"
	"portal/core"
	"portal/model"

	"github.com/labstack/echo"
	mw "github.com/labstack/echo/middleware"
	"github.com/pkg/errors"
)

// WebServer booting web server by configuration
func WebServer(termination model.TermChan, testMode bool) (fn model.DaemonFunc, err error) {
	// check termination channel
	if cap(termination) == 0 {
		err = core.ErrExtTermChanCapInvalid
		return
	}
	/*
		// try to change working dir
		if _, er := changeWorkingDir(); er != nil {
			err = er
			return
		}
	*/

	// check if we need to create admin
	if createAdmin := flag.Lookup("adm"); createAdmin != nil && createAdmin.Value != nil {
		if adm := createAdmin.Value.String(); len(adm) > 0 {
			// 	conf := core.GetConfig()
			//dao.GetUserDAO().Create(context.Background(), core.GetDB(), conf.WebServer.Secure.SipHashSum0, conf.WebServer.Secure.SipHashSum1, adm, "20wPk29bnP2kc93nb92bzEobm")
		}
	}
	// get configs
	mainConf, bindingConf := core.GetConfig(), core.GetBindingConfUnsafe()

	// try to load TLS Config
	var tlsConf *tls.Config
	if len(bindingConf.Cert) > 0 {
		if tlsConf, err = loadTLSConf(bindingConf.Cert, bindingConf.Key); err != nil {
			err = fmt.Errorf("Fail to load cert and key file: %s %s", bindingConf.Cert, bindingConf.Key)
			return
		}
	}

	// Initialize router and http server
	e, server := echo.New(), &http.Server{
		Addr:      fmt.Sprintf(":%d", bindingConf.Port),
		TLSConfig: tlsConf,
	}
	log.Println(bindingConf.Port)

	// Disable echo logging
	e.Logger.SetOutput(ioutil.Discard)

	// Recover middleware recovers from panics anywhere in the chain, prints stack trace and handles the control to the centralized HTTPErrorHandler.
	// Default stack size for trace is 4KB. For more example, please refer to https://echo.labstack.com/
	//e.Use(mw.Recover())

	// Remove trailing slash middleware removes a trailing slash from the request URI.
	e.Pre(mw.RemoveTrailingSlash())

	// Set BodyLimit Middleware. It will panic if fail. For more example, please refer to https://echo.labstack.com/
	e.Use(mw.BodyLimit(mainConf.WebServer.BodyLimit))

	// Secure middleware provides protection against cross-site scripting (XSS) attack, content type sniffing, clickjacking, insecure connection and other code injection attacks.
	// For more example, please refer to https://echo.labstack.com/
	e.Use(mw.Secure())
	/*
		// Restricted group of URIs for
		r := e.Group("/r")
		r.Use(mw.JWTWithConfig(mw.JWTConfig{
			Claims:      &model.Claim{},
			ContextKey:  mainConf.WebServer.Secure.JWT.ContextKey,
			SigningKey:  []byte(mainConf.WebServer.Secure.JWT.SecretKey),
			TokenLookup: "header:authorization",
		}))

		// SecureCookie middleware enable secure cookie feature for authorization
		r.Use(model.NewSecureCookieMW(model.SecureCookieConfig{
			HashKey:    []byte(mainConf.WebServer.Secure.SecureCookie.HashKey),
			BlockKey:   []byte(mainConf.WebServer.Secure.SecureCookie.BlockKey),
			CookieName: mainConf.WebServer.Secure.SecureCookie.CookieName,
			ContextKey: mainConf.WebServer.Secure.SecureCookie.ContextKey,
		}))
		// init router
		initRouter(e, r)
	*/

	initRouter(e)

	// Start server
	go func() {
		if err := e.StartServer(server); err != nil {
			core.LogErr(errors.WithStack(err))
		}
	}()

	fn = func(wg *sync.WaitGroup, termination model.TermChan, testMode bool) {
		defer wg.Done() // no need to prevent defer()

		<-termination

		// try to shutdown server
		if err := e.Shutdown(context.Background()); err != nil {
			core.LogErr(errors.WithStack(err))
		} else {
			core.LogWarning(&model.LogFormat{Action: "Shutdown", Success: "Gracefully stop WebServer"})
		}
	}
	return
}

func initRouter(e *echo.Echo) {
	e.POST("/get/all", stock.GetAllPredictedPrice)
	e.POST("/get/ticket", stock.GetPredictedPriceByTicket)
	e.POST("/get/tickets", stock.GetPredictedPriceByTickets)
}

func loadTLSConf(certFile, keyFile string) (*tls.Config, error) {
	tlsConfig := &tls.Config{
		MinVersion:               tls.VersionTLS12,
		CurvePreferences:         []tls.CurveID{tls.CurveP521, tls.CurveP384, tls.CurveP256},
		PreferServerCipherSuites: true,
		CipherSuites: []uint16{
			tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
			tls.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,
			tls.TLS_RSA_WITH_AES_256_GCM_SHA384,
			tls.TLS_RSA_WITH_AES_256_CBC_SHA,
		},
	}

	tlsConfig.Certificates = make([]tls.Certificate, 1)

	var err error
	if tlsConfig.Certificates[0], err = tls.LoadX509KeyPair(certFile, keyFile); err != nil {
		return nil, err
	}

	return tlsConfig, nil
}
