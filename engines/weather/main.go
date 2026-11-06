// Package main evaluates operational weather guardrails over a bounded JSON input.
package main

import (
 "encoding/json"
 "errors"
 "fmt"
 "io"
 "os"
)

type Input struct {
 Days []Day `json:"days"`
 Heat float64 `json:"heat"`
 Rain float64 `json:"rain"`
 Wind float64 `json:"wind"`
}
type Day struct {
 Date string `json:"date"`
 Temperature *float64 `json:"temperature_c"`
 Rain *float64 `json:"rain_mm"`
 Wind *float64 `json:"wind_kmh"`
 Status string `json:"status"`
 Reasons []string `json:"reasons"`
 Missing bool `json:"missing_data"`
}
type Result struct {
 Days []Day `json:"days"`
 Overall string `json:"overall"`
 Flagged int `json:"flagged_days"`
 Model string `json:"model"`
 Engine string `json:"engine"`
 Thresholds map[string]float64 `json:"thresholds"`
}
func Assess(in Input) (Result,error) {
 if len(in.Days)==0 || len(in.Days)>16 || in.Rain<=0 || in.Wind<=0 { return Result{},errors.New("invalid bounds") }
 result:=Result{Days:in.Days,Overall:"normal",Model:"operational-thresholds-v1",Engine:"go",
   Thresholds:map[string]float64{"heat_c":in.Heat,"rain_mm":in.Rain,"wind_kmh":in.Wind}}
 rank:=map[string]int{"normal":0,"watch":1,"high":2,"unknown":3}
 for i:=range result.Days {
  d:=&result.Days[i];d.Reasons=[]string{}
  if d.Temperature!=nil && *d.Temperature>=in.Heat {d.Reasons=append(d.Reasons,"heat")}
  if d.Rain!=nil && *d.Rain>=in.Rain {d.Reasons=append(d.Reasons,"rain")}
  if d.Wind!=nil && *d.Wind>=in.Wind {d.Reasons=append(d.Reasons,"wind")}
  d.Missing=d.Temperature==nil || d.Rain==nil || d.Wind==nil
  d.Status="normal"
  if len(d.Reasons)==1 {d.Status="watch"};if len(d.Reasons)>=2 {d.Status="high"};if d.Missing {d.Status="unknown"}
  if d.Status=="watch" || d.Status=="high" {result.Flagged++}
  if rank[d.Status]>rank[result.Overall] {result.Overall=d.Status}
 }
 return result,nil
}
func run(in io.Reader,out io.Writer) error {
 decoder:=json.NewDecoder(io.LimitReader(in,1<<20));decoder.DisallowUnknownFields()
 var input Input
 if err:=decoder.Decode(&input);err!=nil{return err}
 result,err:=Assess(input);if err!=nil{return err}
 return json.NewEncoder(out).Encode(result)
}
func main(){if err:=run(os.Stdin,os.Stdout);err!=nil{fmt.Fprintln(os.Stderr,err);os.Exit(1)}}
