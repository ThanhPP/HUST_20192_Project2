package boot

import (
	"os"
	"os/signal"
	"sync"
	"syscall"

	"portal/core"
	"portal/model"
	"portal/webserver"

	log "github.com/sirupsen/logrus"
)

var daemonChans = []model.TermChan{}
var daemonChannelLock sync.Mutex

func registerDaemons(wg *sync.WaitGroup, testMode bool) {
	// register Webserver
	registerDaemon(wg, testMode, webserver.WebServer)
}

func registerDaemon(wg *sync.WaitGroup, testMode bool, halfDaemon model.HalfDaemonFunc) {
	if halfDaemon != nil {
		termChan := model.NewTermChan()
		daemon, err := halfDaemon(termChan, testMode)
		if err != nil {
			panic(err)
		}

		_registerDaemon(wg, termChan, testMode, daemon)
	}
}

func _registerDaemon(wg *sync.WaitGroup, termChan model.TermChan, testMode bool, daemon model.DaemonFunc) {
	if daemon != nil {
		daemonChannelLock.Lock()
		defer daemonChannelLock.Unlock()

		daemonChans = append(daemonChans, termChan)

		wg.Add(1)
		go daemon(wg, termChan, testMode)
	}
}

func killDaemons(sig os.Signal) {
	daemonChannelLock.Lock()
	defer daemonChannelLock.Unlock()

	for i := len(daemonChans) - 1; i >= 0; i-- {
		daemonChans[i] <- sig
	}
}

func Boot(externalTermination model.TermChan, testMode bool) (err error) {
	if cap(externalTermination) == 0 {
		err = core.ErrExtTermChanCapInvalid
		return
	}

	if !testMode {
		log.SetFormatter(&log.JSONFormatter{})
	}

	log.SetOutput(os.Stdout)

	currentDir, err := os.Getwd()
	_ = os.Chdir(currentDir)

	if testMode {
		core.LogInfo(&model.LogFormat{Action: "Boot", Data: "Test mode"})
		// TODO init test DB
	} else {
		core.LogInfo(&model.LogFormat{Action: "Boot", Data: "Production mode"})
		// TODO boot Database construct and config
	}

	/*
		// check err after TODO is done
		if err != nil {
			panic(err)
		}
	*/

	return bootstrapDaemons(externalTermination, testMode)
}
func bootstrapDaemons(extTerm <-chan os.Signal, testMode bool) (err error) {
	defer core.LogWarning(&model.LogFormat{Action: "Shutdown", Success: "Gracefully shutdown daemons"})

	// os signal handling
	sigs := make(chan os.Signal, 10)
	done := make(chan os.Signal, 10)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGQUIT, syscall.SIGKILL, syscall.SIGTERM)

	// waiter all daemons
	var wg sync.WaitGroup

	// register daemons
	registerDaemons(&wg, testMode)

	// catch signal
	go func() {
		select {
		case sig := <-sigs:
			core.LogWarning(&model.LogFormat{Action: "HandleSignal", Data: sig, Source: "Internal"})
			done <- sig
		case sig := <-extTerm:
			core.LogWarning(&model.LogFormat{Action: "HandleSignal", Data: sig, Source: "External"})
			done <- sig
		}
	}()

	// kill daemons
	killDaemons(<-done)

	// wait all daemons done
	wg.Wait()

	return
}
