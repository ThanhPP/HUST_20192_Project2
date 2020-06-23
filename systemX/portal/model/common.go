package model

import (
	"context"
	"database/sql"
	"fmt"
	"net/http"
	"os"
	"sync"

	"github.com/dgrijalva/jwt-go"
	"github.com/gorilla/securecookie"
	"github.com/labstack/echo"
)

// TermChan os.Signal channel for termination
type TermChan chan os.Signal

// NewTermChan create new termination channel with capacity 1
func NewTermChan() TermChan {
	return make(TermChan, 1)
}

// LogFormat log pattern for whole system
type LogFormat struct {
	ServiceName string      `json:"srv"`
	Source      string      `json:"src,omitempty"`
	Action      string      `json:"act,omitempty"`
	Data        interface{} `json:"dat,omitempty"` // data
	Err         interface{} `json:"err,omitempty"` // error
	Success     interface{} `json:"suc,omitempty"` // success
}

// DaemonFunc daemon function
type DaemonFunc func(wg *sync.WaitGroup, termination TermChan, testMode bool)

// HalfDaemonFunc return a daemon function for invoker to do next step
type HalfDaemonFunc func(termination TermChan, testMode bool) (DaemonFunc, error)

// ExecTransaction template to execute transaction
func ExecTransaction(ctx context.Context, tx *sql.Tx, exec func(ctx context.Context, tx *sql.Tx) error) (err error) {
	if err = exec(ctx, tx); err != nil {
		tx.Rollback()
		return
	}

	return tx.Commit()
}

//---------------------------------------- jwt Claim ---------------------------------------------
// Claim jwt claim
type Claim struct {
	Username   string
	Group      []string
	Permission [][]string
	jwt.StandardClaims
}

//---------------------------------------- Secure Cookie ---------------------------------------------
// SecureCookieConfig secure cookie middleware configuration
type SecureCookieConfig struct {
	HashKey    []byte
	BlockKey   []byte
	CookieName string
	ContextKey string
}

type cookieValidator struct {
	secureCookie *securecookie.SecureCookie
	config       *SecureCookieConfig
}

func (c cookieValidator) MakeSecureCookie(val string) (*http.Cookie, error) {
	if c.secureCookie == nil || c.config == nil {
		return nil, fmt.Errorf("CookieValidator not initialized")
	}

	encoded, err := c.secureCookie.Encode(c.config.CookieName, val)
	if err != nil {
		return nil, err
	}

	return &http.Cookie{
		Name:  c.config.CookieName,
		Value: encoded,
	}, nil
}

func (c cookieValidator) ExpireSecureCookie() (*http.Cookie, error) {
	if c.secureCookie == nil || c.config == nil {
		return nil, fmt.Errorf("CookieValidator not initialized")
	}

	return &http.Cookie{
		Name:   c.config.CookieName,
		MaxAge: -1,
	}, nil
}

// CookieValidator ...
var CookieValidator = cookieValidator{}

func readSecureCookie(secureCookie *securecookie.SecureCookie, c echo.Context, cookieName string) (value string, err error) {
	_cookie, err := c.Cookie(cookieName)
	if err != nil {
		return "", err
	}
	cookie := _cookie.Value

	var val string
	err = secureCookie.Decode(cookieName, cookie, &val)
	value = val

	return
}

// NewSecureCookieMW new secure cookie middleware
func NewSecureCookieMW(config SecureCookieConfig) echo.MiddlewareFunc {
	CookieValidator.secureCookie = securecookie.New(config.HashKey, config.BlockKey)

	if len(config.ContextKey) == 0 {
		config.ContextKey = "USER"
	}

	if len(config.CookieName) == 0 {
		config.CookieName = "auth"
	}

	CookieValidator.config = &config

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if cookie, err := readSecureCookie(CookieValidator.secureCookie, c, CookieValidator.config.CookieName); err == nil {
				c.Set(config.ContextKey, cookie)
			} else {
				return echo.ErrUnauthorized
			}

			// Continue the chain of middleware
			return next(c)
		}
	}
}

//------------------------------------------------- HTTP Request -----------------------------------------------
type AllRequest struct {
	From string `json:"from"`
	To   string `json:"to"`
}
type TicketRequest struct {
	Name string `json:"name"`
	From string `json:"from"`
	To   string `json:"to"`
}

type ManyTicketsRequest struct {
	Names []string `json:"names"`
	From  string   `json:"from"`
	To    string   `json:"to"`
}

//--------------------------------------------------- DB obj ----------------------------------------------------
type StockPredicted struct {
	Ticker    string  `json:"ticker" db:"ticker"`
	Price     float32 `json:"price" db:"price"`
	Timestamp string  `json:"timestamp" db:"timestamp"`
}
