package core

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"portal/lib"
	"portal/model"

	"github.com/dgrijalva/jwt-go"
	_ "github.com/go-sql-driver/mysql"
	log "github.com/sirupsen/logrus"
	"github.com/spf13/viper"
)

const (
	DEFAULTPORT = 8806
	testDSN     = "root:123@/test?charset=utf8&collation=utf8_general_ci&parseTime=true&loc=Asia%2FHo_Chi_Minh"
)

var (
	ErrBadRequest = fmt.Errorf("Bad request")

	ErrExtTermChanCapInvalid = fmt.Errorf("Term chan capacity is invalid")

	// ErrDBObjNull indicate DB Object is nil
	ErrDBObjNull = fmt.Errorf("DB Object is nil")
)

//------------------------- LOG UTILS -------------------------
const serviceName = "Portal-api"

// LogInfo information logging
func LogInfo(lg *model.LogFormat) {
	if lg == nil {
		return
	}
	lg.ServiceName = serviceName

	js, _ := json.Marshal(lg)
	log.Infof("%s", js)
}

// LogErr error logging
func LogErr(err error) {
	if err == nil {
		return
	}
	js, _ := json.Marshal(&model.LogFormat{ServiceName: serviceName, Err: err.Error()})
	log.Errorf("%s", js)
}

// LogWarning warning logging
func LogWarning(lg *model.LogFormat) {
	if lg == nil {
		return
	}
	lg.ServiceName = serviceName

	js, _ := json.Marshal(lg)
	log.Infof("%s", js)
}

//---------------------------- Config -----------------------------
// WebServer hold configurations for WebServer
type WebServer struct {
	// BodyLimit The body limit is determined based on both Content-Length request header and actual content read, which makes it super secure.
	// Limit can be specified as 4x or 4xB, where x is one of the multiple from K, M, G, T or P. Example: 2M = 2 Megabyte
	BodyLimit string
	// Secure configuration
	Secure Secure
}

// Config main configuration
type Config struct {
	// WebServer configuration
	WebServer *WebServer `json:"WebServer"`
	// Database configuration
	Database *Database `json:"Database"`
}

type Database struct {
	Address     string
	DBType      string
	DBName      string
	UserName    string
	Password    string
	MaxIdleConn int
	MaxOpenConn int
	IsWsrep     bool
}

// BindingConf binding configuration for webserver
type BindingConf struct {
	Port int
	Cert string
	Key  string
}

// JWTConfig configuration for jwt token within web server
type JWTConfig struct {
	// ContextKey to get JWT token from context
	ContextKey string
	// SecretKey to generate JWT Token
	SecretKey string
	// ExpireInMinute jwt token will expire after minutes
	ExpireInMinute int64
}

// SecureCookie secure cookie configuration
type SecureCookie struct {
	// CookieName name of secure cookie
	CookieName string
	// ContextKey to get SecureCookie from context
	ContextKey string
	// MaxAge of cookie
	MaxAge int
	// ExpireInMinute
	ExpireInMinute int64
	// HashKey 64 character
	HashKey string
	// BlockKey 32 character
	BlockKey string
}

// Secure config
type Secure struct {
	// JWT for web application/mobile
	JWT JWTConfig

	// SecureCookie secure cookie configuration
	SecureCookie SecureCookie

	// SipHashSum0
	SipHashSum0 uint64
	// SipHashSum1
	SipHashSum1 uint64
}

var (
	config = &Config{}
)

// Sign jwt token
func (c *JWTConfig) Sign(claim *model.Claim) (string, error) {
	if claim == nil {
		return "", fmt.Errorf("Claim is nil")
	}

	// modify claim for expire at
	claim.ExpiresAt = time.Now().Add(time.Minute * time.Duration(c.ExpireInMinute)).Unix()
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claim)

	// generate encoded token and send it as response.
	return token.SignedString([]byte(c.SecretKey))
}

// SipHash do sip hash 4-8 sum
func (c *Secure) SipHash(payload []byte) uint64 {
	return uint64(lib.SipHash48(c.SipHashSum0, c.SipHashSum1, payload))
}

var (
	configLock        sync.RWMutex
	serverConf        *Config
	serverBindingConf *BindingConf
)

func init() {
	// if os.Getenv("APP_ENV") == "DEV" {
	viper.SetConfigName("config")
	viper.SetConfigType("toml")
	viper.AddConfigPath(".")
	if err := viper.ReadInConfig(); err != nil {
		panic(err)
	}
	// } else {
	// 	viper.AutomaticEnv()
	// }

	//------------------------- Web Server -------------------------
	serverConf = &Config{
		WebServer: &WebServer{
			BodyLimit: viper.GetString("BODY_LIMIT"),
			Secure: Secure{
				SecureCookie: SecureCookie{
					CookieName:     "auth",
					ContextKey:     "lg_uid",
					MaxAge:         0,
					ExpireInMinute: 1440,
					HashKey:        "Wpdhgkwkpwngapoge93nx9sj2lsigwnx9529xn#px02naigm2-1$93*7nwlwsddf",
					BlockKey:       "DSgjo23058nxg84ns592*383nboiwkg+",
				},
				JWT: JWTConfig{
					ContextKey:     "lg_ctx_key",
					SecretKey:      "Wsjfi^sgjlkajskgwmsmvlk!utwEpc03q<qoP6[%4",
					ExpireInMinute: int64(viper.GetInt("JWT_EXPIRE_TIME")),
				},
				SipHashSum0: 947295729583939162,
				SipHashSum1: 323869573058327753,
			},
		},
		Database: &Database{
			Address:     viper.GetString("SHARD_ADDRESS"),
			DBType:      viper.GetString("SHARD_TYPE"),
			DBName:      viper.GetString("SHARD_NAME"),
			UserName:    viper.GetString("SHARD_USER"),
			Password:    viper.GetString("SHARD_PASSWORD"),
			MaxIdleConn: viper.GetInt("DB_MAX_IDLE"),
			MaxOpenConn: viper.GetInt("DB_MAX_OPEN"),
			IsWsrep:     false,
		},
	}

	serverBindingConf = &BindingConf{
		Port: viper.GetInt("PORT"),
	}

	dns := serverConf.Database.UserName + ":" + serverConf.Database.Password + "@tcp(" + serverConf.Database.Address + ")/" + serverConf.Database.DBName

	dbObj, err := sql.Open(serverConf.Database.DBType, dns)
	if err != nil {
		panic(err)
	}
	SetDB(dbObj)
}

var db *sql.DB
var dbLock sync.RWMutex

func GetDB() (_db *sql.DB) {
	dbLock.RLock()
	_db = db
	dbLock.RUnlock()
	return
}

func SetDB(dbO *sql.DB) {
	dbLock.Lock()
	db = dbO
	dbLock.Unlock()
	return
}

// GetConfig get current configuration for webserver
func GetConfig() (_serverConf *Config) {
	configLock.RLock()
	_serverConf = serverConf
	configLock.RUnlock()
	return
}

// SetConfig set current configuration for webserver
func SetConfig(_serverConf *Config) {
	configLock.RLock()
	serverConf = _serverConf
	configLock.RUnlock()
}

// GetBindingConfUnsafe get webserver binding configuration in unsafe manner, no lock involve
func GetBindingConfUnsafe() *BindingConf {
	return serverBindingConf
}

// SetBindingConfUnsafe set webserver binding configuration in unsafe manner, no lock involve
func SetBindingConfUnsafe(v *BindingConf) {
	serverBindingConf = v
}
