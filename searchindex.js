Search.setIndex({docnames:["api/client-common","api/history-client","api/index","api/misc","api/sink","api/source","glossary","howto/history-client","howto/index","howto/metric-lookup","howto/sink","howto/source","index","metadata"],envversion:{"scanpydoc.definition_list_typed_field":1,"scanpydoc.elegant_typehints":1,"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":1,"sphinx.ext.intersphinx":1,sphinx:56},filenames:["api/client-common.rst","api/history-client.rst","api/index.rst","api/misc.rst","api/sink.rst","api/source.rst","glossary.rst","howto/history-client.rst","howto/index.rst","howto/metric-lookup.rst","howto/sink.rst","howto/source.rst","index.rst","metadata.rst"],objects:{"metricq.Client":{connect:[0,1,1,""],get_metrics:[0,1,1,""],on_signal:[0,1,1,""],run:[0,1,1,""],stop:[0,1,1,""],stopped:[0,1,1,""]},"metricq.HistoryClient":{connect:[1,1,1,""],get_metrics:[1,1,1,""],history_aggregate:[1,1,1,""],history_aggregate_timeline:[1,1,1,""],history_data_request:[1,1,1,""],history_last_value:[1,1,1,""],history_raw_timeline:[1,1,1,""]},"metricq.IntervalSource":{period:[5,1,1,""],update:[5,1,1,""]},"metricq.Sink":{connect:[4,1,1,""],on_data:[4,1,1,""],subscribe:[4,1,1,""]},"metricq.Source":{chunk_size:[5,1,1,""],connect:[5,1,1,""],declare_metrics:[5,1,1,""],flush:[5,1,1,""],send:[5,1,1,""],task:[5,1,1,""]},"metricq.TimeAggregate":{active_time:[3,2,1,""],count:[3,2,1,""],integral:[3,2,1,""],maximum:[3,2,1,""],minimum:[3,2,1,""],sum:[3,2,1,""],timestamp:[3,2,1,""]},"metricq.TimeValue":{timestamp:[3,2,1,""],value:[3,2,1,""]},"metricq.Timedelta":{__str__:[3,1,1,""],from_ms:[3,1,1,""],from_s:[3,1,1,""],from_string:[3,1,1,""],from_timedelta:[3,1,1,""],from_us:[3,1,1,""],ms:[3,1,1,""],ns:[3,1,1,""],s:[3,1,1,""],timedelta:[3,1,1,""],us:[3,1,1,""]},"metricq.Timestamp":{__add__:[3,1,1,""],__eq__:[3,1,1,""],__lt__:[3,1,1,""],__str__:[3,1,1,""],ago:[3,1,1,""],datetime:[3,1,1,""],from_datetime:[3,1,1,""],from_iso8601:[3,1,1,""],from_now:[3,1,1,""],from_posix_seconds:[3,1,1,""],now:[3,1,1,""],posix:[3,1,1,""],posix_ms:[3,1,1,""],posix_ns:[3,1,1,""],posix_us:[3,1,1,""]},"metricq.history_client":{HistoryRequestType:[1,0,1,""],HistoryResponse:[1,0,1,""],HistoryResponseType:[1,0,1,""],InvalidHistoryResponse:[1,0,1,""]},"metricq.history_client.HistoryRequestType":{AGGREGATE:[1,2,1,""],AGGREGATE_TIMELINE:[1,2,1,""],FLEX_TIMELINE:[1,2,1,""],LAST_VALUE:[1,2,1,""]},"metricq.history_client.HistoryResponse":{aggregates:[1,1,1,""],mode:[1,1,1,""],values:[1,1,1,""]},"metricq.history_client.HistoryResponseType":{AGGREGATES:[1,2,1,""],EMPTY:[1,2,1,""],LEGACY:[1,2,1,""],VALUES:[1,2,1,""]},"metricq.source":{MetricSendError:[5,0,1,""]},metricq:{Client:[0,0,1,""],HistoryClient:[1,0,1,""],IntervalSource:[5,0,1,""],Sink:[4,0,1,""],Source:[5,0,1,""],TimeAggregate:[3,0,1,""],TimeValue:[3,0,1,""],Timedelta:[3,0,1,""],Timestamp:[3,0,1,""],rpc_handler:[3,3,1,""]}},objnames:{"0":["py","class","Python class"],"1":["py","method","Python method"],"2":["py","attribute","Python attribute"],"3":["py","decorator","decorator"]},objtypes:{"0":"py:class","1":"py:method","2":"py:attribute","3":"py:decorator"},terms:{"012270469843231":7,"013008404218427":7,"016890013553053":7,"018666244768894":7,"01t00":[3,7],"021740922113744":7,"022798681983203":7,"029395457601895":7,"0298144051392155":7,"02t02":7,"037842717663995":7,"0443300790978025":7,"045782289231323":7,"0495328431393665":7,"052929845492045":7,"055744129198569":7,"059901887791767":7,"06578061778873023":10,"070213303973638":7,"070445673918661":7,"074948972951139":7,"085156064549348":7,"0869138":7,"08725953086385":7,"090598201216997":7,"092209875269113":7,"09505560184217":7,"09832763671875":7,"100":[5,7],"1000":5,"1000000000000000":7,"100hz":9,"100m":7,"103712609":7,"105834719":7,"109231486484054":7,"109705217910005":7,"109750890322914":7,"10min":7,"113817063":7,"11998":7,"1266322950":7,"12v":9,"137031078338623":7,"140197859":7,"1490083450372932":10,"154049873352051":7,"1576000000000000000":7,"1577000000000000000":7,"1577836799998195277":7,"1577836800008200879":7,"1577836800018206481":7,"1577836800028212083":7,"1577836800038217685":7,"1577836800048223287":7,"1577836800058228890":7,"1577836800068234492":7,"1577836800078240094":7,"1577836800088245696":7,"1577836800098251298":7,"1578000000000000000":7,"1579000000000000000":7,"1580000000000000000":7,"1581000000000000000":7,"1582000000000000000":7,"1583000000000000000":7,"1584000000000000000":7,"1585000000000000000":7,"1586000000000000000":7,"1587000000000000000":7,"1588000000000000000":7,"1588509320269324000":10,"1588509321269232000":10,"1588509322269017000":10,"1588509323267878000":10,"1588509324267969000":10,"1589000000000000000":7,"1590000000000000000":7,"1591000000000000000":7,"1592000000000000000":7,"1593000000000000000":7,"1594000000000000000":7,"1595000000000000000":7,"1596000000000000000":7,"1597000000000000000":7,"1598000000000000000":7,"1599000000000000000":7,"1600000000000000000":7,"1601000000000000000":7,"1602000000000000000":7,"1603000000000000000":7,"1604000000000000000":7,"1605000000000000000":7,"1606000000000000000":7,"1607604944653649318":7,"1607605522779676000":7,"1678637":7,"16907605898412":7,"181990750389552":7,"183813638":7,"186786145522286":7,"189763454302634":7,"189800217157934":7,"1970":3,"198339989443255":7,"19898286":7,"19941570890925":7,"19998732":7,"19998746":7,"19998790":7,"19998832":7,"1hz":9,"2018":11,"2019":10,"2020":[7,10],"20e76d0b06769485e428d866a40a19e9":7,"20s":[10,11],"2119":6,"2123122215271":7,"21305943793546":7,"226152306810846":7,"22672075":7,"260790772048024":7,"267878":10,"267969":10,"269017":10,"269232":10,"2692437313689422e":7,"269324":10,"2714809":7,"27197903394699097":7,"275346755981445":7,"2770119258139":7,"28786822296384":7,"2884533":7,"29484596848487854":7,"29932484337397":7,"30919786870951":7,"30d":7,"314934986":7,"317270364484564":7,"325960":7,"33296203613281":7,"336227685213089":7,"3441083":7,"356d":7,"36389875":7,"365":7,"371744397447735":7,"40338314":7,"4122":6,"4169525":7,"4198bdddab794e9f8d774a590651cdc1":6,"421671555":7,"421677696":7,"422114944":7,"4227204663817987":7,"422796585":7,"4230758481433696":7,"4232455502722522":7,"4236512307816254":7,"425685373":7,"42605497043147944":7,"4270007113356799":7,"428285008":7,"428877311":7,"4291822388062562":7,"4297132066602203":7,"430180936":7,"4310744175027674":7,"449131406548784":7,"451322892":7,"4525474207319798":7,"456466462178092":7,"462386484":7,"46617925":7,"46623087":7,"466414451599121":7,"4685728":7,"47610932352675":7,"477295609":7,"4783373487851792":7,"48311378740654076":10,"489314953":7,"4905119547247363":7,"49095530623182":7,"496343":7,"497292058134455":7,"4973650909724805":7,"501395874728":7,"504241073":7,"5051357041124994":7,"5058164":7,"50840513687335":7,"512623432":7,"513875664":7,"5140939976375570":7,"5148844813659733":7,"5185936811198162":7,"522117803":7,"5292031471206438":7,"5332946931093845":7,"53575706482":7,"5427221":7,"54902472030519":7,"55397":7,"555991185":7,"5588739148089780":7,"56394789":7,"566789400":7,"5680943171485073":7,"5691203189059035":7,"5692853013069647":7,"577018180":7,"577035544":7,"577227484":7,"577390774":7,"5781975868653922":7,"5788576471647640":7,"5792219436779407":7,"5794758614134834":7,"58503866":7,"593994374":7,"5998410892025108":7,"599930363353":7,"600963661727302":7,"6042662":7,"604800000000000":3,"6053987":7,"61448812":7,"6226":7,"624169682":7,"62433964":7,"646619296011":7,"6533275":7,"653649":7,"6805707983731595":7,"681345060035232":7,"68548583984375":7,"7010239213612438":7,"71097277085196":7,"71681815":7,"7307683":7,"734305978764959":7,"73528534":7,"7391233":7,"750031412119604":7,"77031535":7,"7771949055949513":10,"779":7,"7939971":7,"82585525512695":7,"848274261152525":7,"855274849":7,"8586157900774826":7,"8599746":7,"8601":[3,13],"86400":3,"8778002158455225":7,"88969261":7,"8951057":7,"9000":6,"9020380477110543":7,"903405893044394":7,"92287374":7,"9249958538284772":7,"93735992":7,"9538565":7,"97846984863281":7,"9841194152832":7,"98658756":7,"991440138904906":7,"99468962":7,"99503304":7,"99565403":7,"99625754":7,"99692006":7,"99702528":7,"99704757":7,"99734524":7,"99748050":7,"99751312":7,"9975132302199418":10,"99759123":7,"99769118":7,"99777911":7,"99790000":7,"99790197":7,"99793322":7,"99795005":7,"99797773":7,"99802606":7,"99804732":7,"99806981":7,"99840737":7,"case":[1,5,6],"catch":1,"class":[0,1,3,4,5,10,11],"default":[0,1,4,10,11],"final":11,"float":[0,4,5,10],"import":[3,5,7,10,11],"int":[0,3,4,5],"long":[3,7],"new":[1,4,5,8,12,13],"return":[0,1,3,4,5,7,9,11],"short":3,"super":[5,10,11],"true":[0,1,3,4,5,7,9,10,11],"while":[5,11],AND:[10,11],ARE:[10,11],BUT:[10,11],FOR:[10,11],For:[6,10,11,13],NOT:[6,10,11],One:3,SUCH:[10,11],THE:[10,11],That:13,The:[0,1,3,5,6,9,10,11,13],Then:7,These:6,USE:[10,11],Use:[0,1,5,6,7],Using:7,__add__:3,__eq__:3,__init__:[5,10,11],__lt__:3,__main__:[10,11],__name__:[10,11],__str__:3,_config:5,_id:[7,13],_metric:10,_on_config:[5,11],_rate:11,_rev:7,a_week_lat:3,abc:9,about:[5,7,10],abov:[10,11],abstractmethod:[4,5],accept:3,access:1,accord:[6,13],accordingli:7,active_tim:[3,7],adapt:11,add:10,add_uuid:[4,10],added:1,addit:[3,6],advis:[5,10,11],affect:5,after:[1,5,10],again:5,age:7,agent:0,agentstoppederror:0,aggreg:[1,2,8,12],aggregate_timelin:1,ago:[3,7],all:[0,1,3,5,7,9,10,11,13],allow:10,almost:[5,7],alreadi:[3,9],altern:[1,9],alwai:9,amqp:[7,10,11],ani:[0,4,5,6,10,11,13],anoth:[3,11],anyth:11,apart:1,api:[9,12],appear:10,append:[4,6],appli:[9,13],applic:6,appropri:[11,13],arbitrari:[5,6,13],arg:[0,1,4,5,10,11],argument:[1,5,9,10],ariel:[7,9],aris:[10,11],arriv:[4,10],asctim:[10,11],associ:[7,13],assum:10,async:[3,5,7,10,11],asynchron:10,asyncio:[5,7,11],attach:[0,5,6],attempt:5,autom:11,automat:[5,10,11],avail:[6,9],averag:[1,7],await:[0,1,4,5,7,9,10,11],awar:[3,5],backend:13,bacnet:11,bandwidth:7,bar:5,base:[0,1,4,7,10],basic_config:[10,11],been:10,befor:[1,3,5,6],behav:[3,7],behavior:1,behaviour:5,being:[5,13],below:[0,1,7,11],best:13,between:[1,5,11],bin:[10,11],binari:[10,11],block:10,board:9,bool:[0,1,4,13],both:[1,7],bright_blu:10,buffer:5,build:[4,5,6,7,8,12],built:11,busi:[10,11],calcul:7,call:[0,1,5,6,9,10,11],callback:[0,4,10,11],can:[5,7,10,11,13],cancel_on_except:0,catch_sign:0,caught:5,caus:[0,5,10,11],certain:3,chang:11,check:3,chronolog:6,chunk:5,chunk_offset:9,chunk_siz:5,classmethod:3,cleanli:1,click:[10,11],click_complet:[10,11],click_log:[10,11],client:[2,3,4,6,7,9,10,11,12],client_vers:0,close:10,code:[5,7,10,11],collect:5,combin:3,command:[10,11],common:[2,11,12],commun:11,compar:[3,7],compens:11,complet:[8,12],complic:[7,11],compon:9,concret:6,condit:[10,11],config:[3,5,11],configur:[3,5,11],connect:[0,1,4,5,6,8,10,11,12],connectfailederror:0,consecut:[1,5,11],consequenti:[10,11],constant:[5,8,12,13],construct:[10,11],constructor:10,consum:[6,13],consumpt:6,contain:[1,3,7,9,10,11],content:[2,12],context:1,continu:11,contract:[10,11],contributor:[10,11],control:5,conveni:11,convert:[1,3,11],copyright:[10,11],core:6,coroutin:11,correct:3,correspond:3,could:1,count:[3,7,13],counter:5,cours:6,cover:[1,7],cpu:[6,11],creat:[3,4,11],current:11,custom:0,cycl:7,dai:[3,7],damag:[10,11],data:[1,4,5,6,8,10,11,12],databas:[7,10,13],datapoint:10,date:[3,7,13],datetim:3,deadlin:5,declar:[5,6,11,13],declare_metr:[5,11,13],decod:1,decor:[3,11],def:[3,5,7,10,11],defin:[4,7,8,12,13],delimit:7,delta:[3,7],depend:[1,9,10,11],deriv:[0,10,11],describ:[3,6,13],descript:[1,5,11,13],design:10,desir:[1,6],detail:[1,6,9,10],determin:1,dict:[0,1,5],dictionari:[0,5,9],differ:[4,9,10,11],dimensionless:13,direct:[10,11],directli:[7,10],disabl:5,disc:6,disclaim:[10,11],displai:[6,13],distinct:[1,6],distinguish:[4,6],distribut:[10,11],document:[1,6,9,10,11],doe:[1,11,13],dram:[7,9],dresden:[10,11],dummi:[10,11],dummysink:10,dummysourc:11,duplic:5,durat:[1,2,7,11,12],duration_str:3,dynam:11,dzzze:9,e13:13,e27:6,each:[1,6,7,10,13],echo:10,effect:3,either:[0,1,5,7,13],elab:[7,9],elaps:3,elif:1,els:1,empti:[1,11,13],encount:0,end:10,end_tim:[1,7],endors:[10,11],ensur:6,enter:11,entri:7,env:[10,11],epoch:3,equival:3,error:11,establish:10,etc:[0,1,3,6,7],even:[5,10,11],event:[10,11],everi:[4,5,10,11],evolv:6,exactli:9,exampl:[3,5,6,7,8,12,13],except:[0,1,2,11,12],exchang:6,execut:5,exemplari:[10,11],exhaust:1,exist:9,expect:3,expens:7,expir:4,explor:7,express:[10,11],extra:[10,11],fail:[1,5],failur:5,fals:[0,1,3,9],fan:9,far:11,feder:[10,11],fetch:[1,8,12],fgh:9,field:[6,12],filter:0,find:10,first:[1,5,7,10,11],fit:[10,11],fix:11,flag:0,flex_timelin:1,flush:5,fmt:[10,11],follow:[6,10,11],foo:5,form:[3,10,11,13],format:[1,3,6,10,11,13],formatt:[10,11],forward:10,free:[6,13],from:[0,1,3,5,10,11,12],from_:[3,5],from_datetim:3,from_iso8601:[3,7],from_m:3,from_now:3,from_posix_second:3,from_str:[3,7],from_timedelta:3,from_u:3,frontend:[6,11],function_tag:3,functool:3,futur:[1,3],gener:[4,5,10,13],germani:[10,11],get:[5,8,10,11,12],get_logg:[10,11],get_metr:[0,1,7,9],get_some_sensor_valu:5,git:[10,11],given:[0,5,9,10],glossari:12,good:[6,10,11],guess:13,had:10,hal:6,hand:1,handl:[0,1,2,4,5,10,11,12,13],handler:[3,10,11],happen:3,has:[1,3,5,10],have:[5,6,7,13],heavi:11,help:11,henc:3,here:[1,7,10,11],hex:6,hint:13,histor:[0,1,8,9,12,13],histori:[2,7,12],history_aggreg:[1,7],history_aggregate_timelin:[1,7],history_cli:1,history_data_request:1,history_last_valu:[1,7],history_raw_timelin:[1,7],historycli:[0,1,3,7],historyrequesttyp:1,historyrespons:1,historyresponsetyp:1,hold:10,holder:[10,11],host:6,hour:[3,7],how:[0,1,4,5,6,7,10,12],howev:[10,11],hta:10,human:[3,13],idea:7,ideal:13,identif:11,identifi:[6,7,10],immedi:5,implement:[3,4,5,6,10,11,13],impli:[10,11],improv:[8,12],incident:[10,11],includ:[0,1,10,11,13],inclus:1,incom:4,increment:5,index:12,indic:[10,11,13],indirect:[10,11],inevit:11,infix:[0,8,12],info:[6,10,11],inform:[0,1,6,7,11,13],inherit:0,init:[10,11],initi:[5,10,11],instal:[10,11],instanc:[3,4,6,7,10],instead:[5,7,10,11],integr:[3,7],intend:4,interest:[1,7,10],interfac:[9,10],interpret:[1,6],interrupt:[10,11],interv:[5,11],interval_max:[1,7],intervalsourc:[3,5,8,12],introduct:4,invalid:[1,3,5],invalidhistoryrespons:1,invok:[0,4],ipmi:11,iso:[3,13],iso_str:3,issu:11,iter:[1,7],its:[0,5,6,10,11],json:[6,11,13],just:10,kebab:6,keep:[5,10],kei:[0,5,6,13],keyword:5,kib:13,kind:11,know:[9,10],known:13,kwarg:[0,1,4,5,10,11],last:[1,8,12,13],last_valu:1,latenc:5,later:3,legaci:1,less:11,let:10,level:11,levelnam:[10,11],liabil:[10,11],liabl:[10,11],librari:[11,12],lift:11,like:[1,3,6,10,11],limit:[0,7,9,10,11],line:[10,11],list:[0,1,4,9,10,11],lmg670:7,load:5,local:3,local_offset:9,localhost:[10,11],log:[10,11],logger:[10,11],longer:[5,7],lookup:[7,8,12],loss:[10,11],low:11,made:5,mai:[5,6,10,11,13],main:5,make:[1,10,11,13],manag:[6,13],management_url:[10,11],mani:6,manual:5,map:[0,5,9],mark:3,match:[0,1,3,9],materi:[10,11],max_interv:1,maximum:[0,1,3,7],mean:[1,5,13],measur:[4,5,6,11,13],measurand:6,memori:11,merchant:[10,11],messag:[10,11],met:[10,11],metadata:[0,4,5,6,8,9,11,12],method:[0,1,3,4,5,9,10,11],metric:[0,1,3,4,5,6,8,10,11,12],metricq:[0,1,3,4,5,6,7,8,13],metricq_sink:10,metricq_sourc:11,metricsenderror:[5,11],microsecond:3,might:[1,13],million:7,millisecond:3,min:3,minim:11,minimum:[1,3,7],minut:[3,5,7],miscellan:[2,12],miss:5,mode:1,modif:[10,11],modul:12,monitor:[10,11],more:[6,7,9,11],most:[1,6,7],much:5,multipl:[1,5,6,8,10,12],must:[5,6,10,11],mysourc:[3,5],name:[0,1,3,4,5,6,9,10,11,13],nanosecond:3,necessari:[6,13],need:[4,7,9,10,11,13],neg:3,neglig:[10,11],neither:[10,11],network:[0,1,4,5,6,8,9,10,11,12,13],next:[5,13],night:3,non:[1,9],none:[0,1,4,5,11],nor:[10,11],note:7,notic:[10,11],now:[3,5,7,10,11],number:[0,3,5,7,11,13],numer:10,object:3,obtain:[7,10,11],occur:0,off:5,offend:0,offset:3,omit:[1,7,13],on_config:[3,5],on_data:[4,10],on_sign:0,onc:[5,10,11],one:[1,5,6,13],ones:1,onli:[0,1,3,7,11],onlin:6,onward:1,oper:[1,2,3,12],optim:6,option:[0,1,4,5,6,10,11],order:[1,3,6],org:7,other:[0,3,6,10,11],otherwis:[0,5,9,10,11],our:[7,10,11],out:[10,11],output:10,over:[1,3,6,7,11],overhead:5,overrid:[0,4,5,10,11],overview:7,overwritten:13,own:[6,7],owner:[10,11],packag:9,packet:5,page:[10,12],pair:[1,2,6,12,13],paramet:[0,1,3,4,5],pars:3,part:0,particular:[5,10,11],pass:[0,1,7,9,10,11],past:[3,7],pattern:[0,1],pcre:9,per:[5,11,13],perfectli:13,perform:6,period:[3,5,7,11],permiss:[10,11],permit:[10,11],persist:10,pick:5,pip:[10,11,12],place:10,plain:[9,11],point:[1,4,5,6,7,10,11,13],posix:3,posix_m:3,posix_n:3,posix_u:3,possibl:[3,10,11],power:[7,9,13],precise_str:7,prefix:[0,6,8,12,13],print:[3,7,9,10,11],prior:[10,11],process:10,procur:[10,11],produc:[5,6,13],product:[10,11],profit:[10,11],program:11,promot:[10,11],properti:6,proto:1,protocol:[10,11],provid:[1,5,6,7,9,10,11],pull:11,purpos:[10,11],put:5,pypi:12,python3:[10,11],python:11,quantiti:[11,13],queri:7,queue:4,quick:6,quit:11,rack:13,rad:13,rais:[0,1,3,5,11],randint:5,random:[5,11],randomli:4,rang:7,rate:[5,7,8,12,13],raw:[1,8,12],raw_tv:7,read:[5,11],readabl:[3,13],readi:7,real:3,receiv:[0,1,3,4,5,6,10,11],recent:1,recommend:[6,11],record:1,redistribut:[10,11],reduc:5,refer:[3,12],regex:[0,8,12],regist:1,regular:5,rel:3,relat:[3,6,11,13],relev:5,remain:[1,5],replac:11,repo:[10,11],represent:3,reproduc:[10,11],republ:[10,11],request:[1,6,10],request_dur:1,request_typ:1,requir:[6,10,11],rerais:0,reserv:[10,11,12],respect:13,respons:[0,1,4,5,6],restart:[5,11],restrict:13,result:[0,3,5,7,9],retain:[10,11],retriev:[0,1,7,9],rfc:6,right:[5,10,11],room:[6,13],rough:7,rpc:[2,4,6,11,12],rpc_handler:[3,5,11],run:[0,5,8,12],run_history_cli:7,run_until_complet:7,same:[3,4,5,6,10,13],sampl:13,sata:9,save:[7,11],schedul:0,scope:[7,13],script:10,search:[8,12],second:[0,1,3,4,5,11,13],section:6,see:[0,1,3,4,5,6,7,9,10,11],segment:13,select:1,selector:[0,1,9],self:[3,5,10,11],send:[1,5,11],sensor:11,sent:[5,6,10,11],separ:9,sequenc:[0,1],seri:6,server:[7,10,11],servic:[10,11],set:[0,1,5,6,10,11,13],setlevel:[10,11],setup:11,sever:6,shall:[6,10,11],share:10,shorter:3,should:[1,3,5,6,10,13],shown:13,sigint:0,signal:0,sigterm:0,similarli:11,simpl:[10,11],simple_verbosity_opt:[10,11],simpli:11,sinc:[3,7],singl:[1,6,13],sink:[0,2,3,6,7,8,11,12],situat:11,skip:5,sleep:[5,11],softwar:[10,11],some:[5,7,11,13],some_arbitrary_metadata:5,some_sensor:5,somesensorsourc:5,someth:10,sometim:6,sourc:[0,2,3,6,7,8,10,12,13],space:6,span:[1,3,7],special:[10,11,13],specif:[6,7,10,11],specifi:[1,3,5],src:11,standard:[3,10,12],start:[0,1,3,5,9,11,13],start_tim:[1,7],staticmethod:3,step:1,still:7,stop:0,storag:[10,13],store:[10,13],str:[0,1,3,4,5,10],strategi:9,stream:6,strict:[10,11],strictli:6,string:[3,5,6,9,11,13],strongli:11,strptime:3,style:[9,10],subclass:[4,10,11],subscrib:[4,10],substitut:[10,11],success:7,suffix:6,sum:[3,7,9],summar:[8,12],summari:3,superclass:10,suppli:[3,11],support:[3,7,9],suppos:6,sure:[1,10,11],symbol:13,sysinfo:[6,11],system:[6,11],take:5,task:[5,6,11],technisch:[10,11],tell:[10,11],temperatur:[5,6,13],tempor:13,term:10,test:[10,11],than:[3,5],thei:[5,6,10,11],them:[5,7],theori:[10,11],theses:0,thi:[0,1,3,4,5,6,7,9,10,11,12,13],those:9,though:[10,13],through:7,time:[1,2,4,5,6,7,10,11,12,13],timeaggreg:[1,3,7],timedelta:[1,2,5,7,12],timelin:1,timeout:[0,1],timepoint:[4,5],timespan:1,timestamp:[1,2,4,5,7,10,11,12],timevalu:[1,3,7],timezon:3,togeth:[1,3],token:[4,6,7,10,11,13],too:5,tool:13,tort:[10,11],total:3,total_ord:3,track:10,trade:5,transpar:1,treat:13,tri:11,trigger:[5,11],turn:5,two:[3,6,10],type:[0,1,3,4,5,6,10],typic:13,underli:[1,5],unexpectedli:0,unhandl:0,union:[0,1,4],uniqu:[6,10,11],unit:[3,5,7,11,13],universitaet:[10,11],unix:3,unless:1,unpack:3,unsent:5,unspecifi:1,until:[5,7,10],updat:[5,11,13],url:[7,11],usag:11,use:[5,7,10,11,12,13],used:[10,11,13],useful:[4,7,9,11,13],user:[4,5,7],uses:7,using:[5,6,8,12],usr:[10,11],usual:11,utc:3,util:[6,11],uuid:[4,6],valid:[6,13],valu:[1,2,4,5,6,8,10,11,12,13],valueerror:[1,3],version:6,via:[0,11],visual:10,voltag:[9,13],wai:[7,10,11,13],wait:0,want:[5,7,9,11],warranti:[10,11],web:6,websocket:6,well:7,went:7,were:0,what:10,when:[0,3,5,13],where:[6,7,11,13],whether:[1,3,4,10,11,13],which:[1,4,5,7,10,11,13],whole:3,whose:9,within:[1,3],without:[5,7,10,11],wizard:11,won:[7,10,11],word:6,work:[9,11],worri:[5,10],would:[3,11,13],wouldn:11,wrap:7,written:[6,10,11],wrong:1,year:7,yet:9,yield:[1,3],you:[0,3,5,7,9,10],your:[5,6],zih:[10,11],zzz:9},titles:["Common client operation","History Client","API Reference","Miscellaneous","Sink","Source","Glossary","Fetching historical metric data","How to use this library","Metric lookup","Building a MetricQ Sink","Building a MetricQ Source","Welcome to MetricQ\u2019s documentation!","Metric Metadata"],titleterms:{"new":[10,11],aggreg:[3,7],api:2,build:[10,11],client:[0,1],common:0,complet:[10,11],connect:7,constant:11,data:7,defin:[10,11],document:12,durat:3,exampl:[10,11],except:5,fetch:7,field:13,get:7,glossari:6,handl:3,histor:7,histori:1,how:8,improv:11,indic:12,infix:9,instal:12,intervalsourc:11,last:7,librari:8,lookup:9,metadata:[7,13],metric:[7,9,13],metricq:[10,11,12],miscellan:3,multipl:7,network:7,oper:0,pair:3,prefix:9,quickstart:12,rate:11,raw:7,refer:2,regex:9,reserv:13,rpc:3,run:[10,11],search:9,sink:[4,10],sourc:[5,11],standard:13,summar:7,tabl:12,thi:8,time:3,timedelta:3,timestamp:3,use:8,using:[10,11],valu:[3,7],welcom:12}})