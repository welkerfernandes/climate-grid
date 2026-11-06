package main
import("strings";"testing";"bytes")
func ptr(n float64)*float64{return &n}
func TestGuardrails(t *testing.T){
 r,e:=Assess(Input{Days:[]Day{{Date:"2030-01-01",Temperature:ptr(38),Rain:ptr(30),Wind:ptr(50)}},Heat:35,Rain:25,Wind:45})
 if e!=nil||r.Overall!="high"||r.Flagged!=1||len(r.Days[0].Reasons)!=3{t.Fatalf("unexpected result: %+v %v",r,e)}
}
func TestUnknown(t *testing.T){
 r,_:=Assess(Input{Days:[]Day{{Rain:ptr(0),Wind:ptr(0)}},Heat:35,Rain:25,Wind:45})
 if r.Overall!="unknown"{t.Fatal("missing data must prevent all-clear")}
}
func TestInvalidInput(t *testing.T){var out bytes.Buffer;if run(strings.NewReader(`{"unexpected":1}`),&out)==nil{t.Fatal("expected rejection")}}
