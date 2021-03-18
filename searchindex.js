Search.setIndex({docnames:["api/client-common","api/exceptions","api/history-client","api/index","api/misc","api/sink","api/source","glossary","howto/history-client","howto/index","howto/metric-lookup","howto/sink","howto/source","index","metadata"],envversion:{"scanpydoc.definition_list_typed_field":1,"scanpydoc.elegant_typehints":1,"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,sphinx:56},filenames:["api/client-common.rst","api/exceptions.rst","api/history-client.rst","api/index.rst","api/misc.rst","api/sink.rst","api/source.rst","glossary.rst","howto/history-client.rst","howto/index.rst","howto/metric-lookup.rst","howto/sink.rst","howto/source.rst","index.rst","metadata.rst"],objects:{"metricq.Client":{connect:[0,1,1,""],get_metrics:[0,1,1,""],on_signal:[0,1,1,""],rpc:[0,1,1,""],run:[0,1,1,""],stop:[0,1,1,""],stopped:[0,1,1,""]},"metricq.HistoryClient":{connect:[2,1,1,""],get_metrics:[2,1,1,""],history_aggregate:[2,1,1,""],history_aggregate_timeline:[2,1,1,""],history_data_request:[2,1,1,""],history_last_value:[2,1,1,""],history_raw_timeline:[2,1,1,""]},"metricq.IntervalSource":{period:[6,1,1,""],update:[6,1,1,""]},"metricq.Sink":{connect:[5,1,1,""],on_data:[5,1,1,""],subscribe:[5,1,1,""]},"metricq.Source":{chunk_size:[6,2,1,""],connect:[6,1,1,""],declare_metrics:[6,1,1,""],flush:[6,1,1,""],send:[6,1,1,""],task:[6,1,1,""]},"metricq.TimeAggregate":{active_time:[4,2,1,""],count:[4,2,1,""],from_value_pair:[4,1,1,""],integral:[4,1,1,""],integral_ns:[4,2,1,""],integral_s:[4,1,1,""],maximum:[4,2,1,""],minimum:[4,2,1,""],sum:[4,2,1,""],timestamp:[4,2,1,""]},"metricq.TimeValue":{timestamp:[4,2,1,""],value:[4,2,1,""]},"metricq.Timedelta":{__floordiv__:[4,1,1,""],__str__:[4,1,1,""],__truediv__:[4,1,1,""],from_ms:[4,1,1,""],from_s:[4,1,1,""],from_string:[4,1,1,""],from_timedelta:[4,1,1,""],from_us:[4,1,1,""],ms:[4,1,1,""],ns:[4,1,1,""],s:[4,1,1,""],timedelta:[4,1,1,""],us:[4,1,1,""]},"metricq.Timestamp":{__add__:[4,1,1,""],__eq__:[4,1,1,""],__lt__:[4,1,1,""],__str__:[4,1,1,""],ago:[4,1,1,""],datetime:[4,1,1,""],from_datetime:[4,1,1,""],from_iso8601:[4,1,1,""],from_now:[4,1,1,""],from_posix_seconds:[4,1,1,""],now:[4,1,1,""],posix:[4,1,1,""],posix_ms:[4,1,1,""],posix_ns:[4,1,1,""],posix_us:[4,1,1,""]},"metricq.exceptions":{AgentStopped:[1,4,1,""],ConnectFailed:[1,4,1,""],HistoryError:[1,4,1,""],InvalidHistoryResponse:[1,4,1,""],MessageError:[1,4,1,""],NonMonotonicTimestamps:[1,4,1,""],PublishFailed:[1,4,1,""],RPCError:[1,4,1,""],ReceivedSignal:[1,4,1,""],ReconnectTimeout:[1,4,1,""],RemoteError:[1,4,1,""]},"metricq.history_client":{HistoryRequestType:[2,0,1,""],HistoryResponse:[2,0,1,""],HistoryResponseType:[2,0,1,""],InvalidHistoryResponse:[2,0,1,""]},"metricq.history_client.HistoryRequestType":{AGGREGATE:[2,2,1,""],AGGREGATE_TIMELINE:[2,2,1,""],FLEX_TIMELINE:[2,2,1,""],LAST_VALUE:[2,2,1,""]},"metricq.history_client.HistoryResponse":{aggregates:[2,1,1,""],mode:[2,1,1,""],values:[2,1,1,""]},"metricq.history_client.HistoryResponseType":{AGGREGATES:[2,2,1,""],EMPTY:[2,2,1,""],LEGACY:[2,2,1,""],VALUES:[2,2,1,""]},metricq:{Client:[0,0,1,""],HistoryClient:[2,0,1,""],IntervalSource:[6,0,1,""],Sink:[5,0,1,""],Source:[6,0,1,""],TimeAggregate:[4,0,1,""],TimeValue:[4,0,1,""],Timedelta:[4,0,1,""],Timestamp:[4,0,1,""],exceptions:[1,3,0,"-"],rpc_handler:[4,5,1,""]}},objnames:{"0":["py","class","Python class"],"1":["py","method","Python method"],"2":["py","attribute","Python attribute"],"3":["py","module","Python module"],"4":["py","exception","Python exception"],"5":["py","decorator","decorator"]},objtypes:{"0":"py:class","1":"py:method","2":"py:attribute","3":"py:module","4":"py:exception","5":"py:decorator"},terms:{"012270469843231":8,"013008404218427":8,"016890013553053":8,"018666244768894":8,"01t00":[4,8],"021740922113744":8,"022798681983203":8,"029395457601895":8,"0298144051392155":8,"02t02":8,"037842717663995":8,"0443300790978025":8,"045782289231323":8,"0495328431393665":8,"052929845492045":8,"055744129198569":8,"059901887791767":8,"06578061778873023":11,"070213303973638":8,"070445673918661":8,"074948972951139":8,"085156064549348":8,"0869138":8,"08725953086385":8,"090598201216997":8,"092209875269113":8,"09505560184217":8,"09832763671875":8,"100":[6,8],"1000":6,"1000000000000000":8,"100hz":10,"100m":8,"103712609":8,"105834719":8,"109231486484054":8,"109705217910005":8,"109750890322914":8,"10min":8,"113817063":8,"11998":8,"1266322950":8,"12v":10,"137031078338623":8,"140197859":8,"1490083450372932":11,"154049873352051":8,"1576000000000000000":8,"1577000000000000000":8,"1577836799998195277":8,"1577836800008200879":8,"1577836800018206481":8,"1577836800028212083":8,"1577836800038217685":8,"1577836800048223287":8,"1577836800058228890":8,"1577836800068234492":8,"1577836800078240094":8,"1577836800088245696":8,"1577836800098251298":8,"1578000000000000000":8,"1579000000000000000":8,"1580000000000000000":8,"1581000000000000000":8,"1582000000000000000":8,"1583000000000000000":8,"1584000000000000000":8,"1585000000000000000":8,"1586000000000000000":8,"1587000000000000000":8,"1588000000000000000":8,"1588509320269324000":11,"1588509321269232000":11,"1588509322269017000":11,"1588509323267878000":11,"1588509324267969000":11,"1589000000000000000":8,"1590000000000000000":8,"1591000000000000000":8,"1592000000000000000":8,"1593000000000000000":8,"1594000000000000000":8,"1595000000000000000":8,"1596000000000000000":8,"1597000000000000000":8,"1598000000000000000":8,"1599000000000000000":8,"1600000000000000000":8,"1601000000000000000":8,"1602000000000000000":8,"1603000000000000000":8,"1604000000000000000":8,"1605000000000000000":8,"1606000000000000000":8,"1607604944653649318":8,"1607605522779676000":8,"1678637":8,"16907605898412":8,"181990750389552":8,"183813638":8,"186786145522286":8,"189763454302634":8,"189800217157934":8,"1970":4,"198339989443255":8,"19898286":8,"19941570890925":8,"19998732":8,"19998746":8,"19998790":8,"19998832":8,"1hz":10,"2018":12,"2019":11,"2020":[8,11],"20e76d0b06769485e428d866a40a19e9":8,"20s":[11,12],"2119":7,"2123122215271":8,"21305943793546":8,"226152306810846":8,"22672075":8,"255":2,"260790772048024":8,"267878":11,"267969":11,"269017":11,"269232":11,"2692437313689422e":8,"269324":11,"2714809":8,"27197903394699097":8,"275346755981445":8,"2770119258139":8,"28786822296384":8,"2884533":8,"29484596848487854":8,"29932484337397":8,"30919786870951":8,"30d":8,"314934986":8,"317270364484564":8,"325960":8,"33296203613281":8,"333333333":4,"3333333333n":4,"336227685213089":8,"3441083":8,"356d":8,"36389875":8,"365":8,"371744397447735":8,"40338314":8,"4122":7,"4169525":8,"4198bdddab794e9f8d774a590651cdc1":7,"421671555":8,"421677696":8,"422114944":8,"4227204663817987":8,"422796585":8,"4230758481433696":8,"4232455502722522":8,"4236512307816254":8,"425685373":8,"42605497043147944":8,"4270007113356799":8,"428285008":8,"428877311":8,"4291822388062562":8,"4297132066602203":8,"430180936":8,"4310744175027674":8,"449131406548784":8,"451322892":8,"4525474207319798":8,"456466462178092":8,"462386484":8,"46617925":8,"46623087":8,"466414451599121":8,"4685728":8,"47610932352675":8,"477295609":8,"4783373487851792":8,"48311378740654076":11,"489314953":8,"4905119547247363":8,"49095530623182":8,"496343":8,"497292058134455":8,"4973650909724805":8,"501395874728":8,"504241073":8,"5051357041124994":8,"5058164":8,"50840513687335":8,"512623432":8,"513875664":8,"5140939976375570":8,"5148844813659733":8,"5185936811198162":8,"522117803":8,"5292031471206438":8,"5332946931093845":8,"53575706482":8,"5427221":8,"54902472030519":8,"55397":8,"555991185":8,"5588739148089780":8,"56394789":8,"566789400":8,"5680943171485073":8,"5691203189059035":8,"5692853013069647":8,"577018180":8,"577035544":8,"577227484":8,"577390774":8,"5781975868653922":8,"5788576471647640":8,"5792219436779407":8,"5794758614134834":8,"58503866":8,"593994374":8,"5998410892025108":8,"599930363353":8,"600963661727302":8,"6042662":8,"604800000000000":4,"6053987":8,"61448812":8,"6226":8,"624169682":8,"62433964":8,"646619296011":8,"6533275":8,"653649":8,"6805707983731595":8,"681345060035232":8,"68548583984375":8,"7010239213612438":8,"71097277085196":8,"71681815":8,"7307683":8,"734305978764959":8,"73528534":8,"7391233":8,"750031412119604":8,"77031535":8,"7771949055949513":11,"779":8,"7939971":8,"82585525512695":8,"848274261152525":8,"855274849":8,"8586157900774826":8,"8599746":8,"8601":[4,14],"86400":4,"8778002158455225":8,"88969261":8,"8951057":8,"9000":7,"9020380477110543":8,"903405893044394":8,"92287374":8,"9249958538284772":8,"93735992":8,"9538565":8,"97846984863281":8,"9841194152832":8,"98658756":8,"991440138904906":8,"99468962":8,"99503304":8,"99565403":8,"99625754":8,"99692006":8,"99702528":8,"99704757":8,"99734524":8,"99748050":8,"99751312":8,"9975132302199418":11,"99759123":8,"99769118":8,"99777911":8,"99790000":8,"99790197":8,"99793322":8,"99795005":8,"99797773":8,"99802606":8,"99804732":8,"99806981":8,"99840737":8,"byte":2,"case":[2,6,7],"catch":2,"class":[0,1,2,4,5,6,11,12],"default":[0,2,5,11,12],"final":12,"float":[0,4,5,6,11],"function":0,"import":[4,6,8,11,12],"int":[0,4,5,6],"long":[4,8],"new":[2,5,6,9,13,14],"null":14,"return":[0,1,2,4,5,6,8,10,12],"short":4,"super":[6,11,12],"true":[0,2,4,5,6,8,10,11,12],"while":[6,12],AND:[11,12],ARE:[11,12],BUT:[11,12],FOR:[11,12],For:[7,11,12,14],NOT:[7,11,12],One:4,SUCH:[11,12],THE:[11,12],That:14,The:[0,1,2,4,6,7,10,11,12,14],Then:8,There:1,These:7,USE:[11,12],Use:[0,2,4,6,7,8],Using:8,__add__:4,__eq__:4,__floordiv__:4,__init__:[6,11,12],__lt__:4,__main__:[11,12],__mul__:4,__name__:[11,12],__str__:4,__truediv__:4,_config:6,_id:[8,14],_metric:11,_on_config:[6,12],_rate:12,_rev:8,a_week_lat:4,abc:10,about:[6,8,11],abov:[11,12],abstractmethod:[5,6],accept:4,access:2,accord:[7,14],accordingli:8,activ:4,active_tim:[4,8],adapt:12,add:11,add_uuid:[5,11],added:2,addit:[0,4,7],advis:[6,11,12],affect:6,after:[2,6,11],again:6,age:8,agent:[0,1],agentstop:1,agentstoppederror:0,aggreg:[2,3,9,13],aggregate_timelin:2,ago:[4,8],all:[0,2,4,6,8,10,11,12,14],allow:[0,11],almost:[6,8],alreadi:[4,10],altern:[2,10],alwai:[1,10],amqp:[8,11,12],ani:[0,5,6,7,11,12,14],anoth:[4,12],anyth:12,apart:2,api:[1,10,13],appear:11,append:[5,7],appli:[10,14],applic:7,appropri:[12,14],arbitrari:[6,7,14],arg:[0,1,2,5,6,11,12],argument:[0,2,4,6,10,11],ariel:[8,10],aris:[11,12],arriv:[5,11],asctim:[11,12],assert:[1,4],assertionerror:1,associ:[8,14],assum:11,async:[4,6,8,11,12],asynchron:11,asyncio:[6,8,12],attach:[0,1,7],attempt:[1,6],attribut:4,autom:12,automat:[6,11,12],avail:[7,10],averag:[2,8],await:[0,2,5,6,8,10,11,12],awar:[4,6],backend:14,bacnet:12,bandwidth:8,bar:6,base:[0,2,4,5,8,11],basic_config:[11,12],been:11,befor:[2,4,6,7],behav:[4,8],behavior:2,behaviour:6,being:[6,14],below:[0,2,8,12],best:14,between:[2,6,12,14],bin:[11,12],binari:[11,12],block:11,board:10,bool:[0,2,5,14],both:[2,8],bright_blu:11,buffer:6,build:[5,6,7,8,9,13],built:[1,12],busi:[11,12],calcul:8,call:[0,2,6,7,10,11,12],callback:[0,5,11,12],can:[6,8,11,12,14],cancel_on_except:0,catch_sign:0,caught:6,caus:[0,1,11,12],certain:4,chang:12,check:[1,4],chronolog:7,chunk:[6,14],chunk_offset:10,chunk_siz:[6,14],chunksiz:14,classmethod:4,cleanli:2,cleanup_on_respons:0,click:[11,12],click_complet:[11,12],click_log:[11,12],client:[3,4,5,7,8,10,11,12,13],client_vers:0,close:11,code:[1,6,8,11,12],collect:6,combin:4,command:[11,12],common:[3,12,13],commun:12,compar:[4,8],compens:12,complet:[9,13],complic:[8,12],compon:10,concret:7,condit:[11,12],config:[4,6,12],configur:[4,6,12],connect:[0,1,2,5,6,7,9,11,12,13],connectfail:[0,1],consecut:[2,6,12],consequenti:[11,12],constant:[6,9,13,14],construct:[11,12],constructor:11,consum:[7,14],consumpt:7,contain:[2,4,8,10,11,12],content:[3,13],context:2,continu:12,contract:[11,12],contrari:1,contributor:[11,12],control:6,conveni:12,convert:[2,4,12],copyright:[11,12],core:7,coroutin:12,correct:4,correspond:4,could:[0,1,2],count:[4,8,14],counter:6,cours:7,cover:[2,8],cpu:[7,12],creat:[4,5,12],current:12,custom:[0,1],cycl:8,dai:[4,8],damag:[11,12],data:[2,5,6,7,9,11,12,13,14],databas:[1,8,11,14],datapoint:11,date:[4,8,14],datetim:4,deadlin:6,declar:[6,7,12,14],declare_metr:[6,12,14],decod:[1,2],decor:[4,12],def:[4,6,8,11,12],defin:[1,5,8,9,13,14],delimit:8,delta:[4,8],depend:[2,10,11,12],deprec:4,deriv:[0,11,12],describ:[4,7,14],descript:[2,6,12,14],design:11,desir:[2,7],detail:[2,7,10,11],determin:2,dict:[0,2,6],dictionari:[0,6,10],differ:[5,10,11,12],dimensionless:14,direct:[11,12],directli:[8,11],disabl:6,disc:7,disclaim:[11,12],displai:[7,14],distinct:[2,7],distinguish:[5,7],distribut:[11,12],divid:4,divis:4,document:[2,7,10,11,12],doe:[2,12,14],dram:[8,10],dresden:[11,12],dummi:[11,12],dummysink:11,dummysourc:12,duplic:6,durat:[2,3,8,12,13],duration_str:4,dynam:12,dzzze:10,e13:14,e27:7,each:[2,7,8,11,14],echo:11,effect:4,either:[0,1,2,6,8,14],elab:[8,10],elaps:4,elif:2,els:2,empti:[2,12,14],encount:0,end:11,end_tim:[2,8],endors:[11,12],ensur:7,enter:12,entri:8,env:[11,12],epoch:4,equival:4,error:[0,1,4,12],establish:11,estim:14,etc:[0,2,4,7,8],even:[6,11,12],event:[11,12],everi:[5,6,11,12],evolv:7,exactli:10,exampl:[4,6,7,8,9,13,14],except:[0,2,3,6,12,13],exchang:[0,1,7],execut:6,exemplari:[11,12],exhaust:2,exist:10,expect:[4,14],expens:8,expir:5,explicit:4,explor:8,express:[11,12],extra:[11,12],extra_messag:[1,2],factor:4,fail:[1,2,6],failur:6,fals:[0,2,4,10],fan:10,far:12,feder:[11,12],fetch:[2,9,13],fgh:10,field:[7,13],filter:0,find:11,first:[2,6,8,11,12],fit:[11,12],fix:12,flag:0,flex_timelin:2,floor:4,flush:6,fmt:[11,12],follow:[7,11,12],foo:6,form:[4,11,12,14],format:[2,4,7,11,12,14],formatt:[11,12],forward:[0,11],free:[7,14],from:[0,2,4,6,11,12,13],from_:[4,6],from_datetim:4,from_iso8601:[4,8],from_m:4,from_now:4,from_posix_second:4,from_str:[4,8],from_timedelta:4,from_u:4,from_value_pair:4,frontend:[7,12],function_tag:4,functool:4,futur:[2,4],gener:[1,5,6,11,14],germani:[11,12],get:[6,9,11,12,13],get_logg:[11,12],get_metr:[0,2,8,10],get_some_sensor_valu:6,git:[11,12],give:14,given:[0,6,10,11],glossari:13,good:[7,11,12],guess:14,had:11,hal:7,hand:2,handl:[0,2,3,5,6,11,12,13,14],handler:[4,11,12],happen:4,has:[1,2,4,6,11],have:[4,6,7,8,14],heavi:12,help:12,henc:4,here:[2,8,11,12],hex:7,hint:14,histor:[0,2,9,10,13,14],histori:[1,3,8,13],history_aggreg:[2,8],history_aggregate_timelin:[2,8],history_cli:2,history_data_request:2,history_last_valu:[2,8],history_raw_timelin:[2,8],historycli:[0,2,4,8],historyerror:1,historyrequesttyp:2,historyrespons:2,historyresponsetyp:2,hold:11,holder:[11,12],host:7,hour:[4,8],how:[0,2,5,6,7,8,11,13],howev:[11,12],hta:11,human:[4,14],idea:8,ideal:14,identif:12,identifi:[7,8,11],immedi:6,implement:[4,5,6,7,11,12,14],impli:[11,12],improv:[9,13],incident:[11,12],includ:[0,2,11,12,14],inclus:2,incom:5,increas:2,increment:6,index:13,indic:[11,12,14],indirect:[11,12],individu:6,inevit:12,infix:[0,9,13],info:[7,11,12],inform:[0,2,7,8,12,14],inherit:0,init:[11,12],initi:[6,11,12],input:1,instal:[11,12],instanc:[4,5,7,8,11],instead:[6,8,11,12],integ:[4,6],integr:[4,8],integral_:4,integral_n:4,intend:5,interact:1,interest:[2,8,11],interfac:[10,11],interpret:[2,7],interrupt:[11,12],interv:[6,12],interval_max:[2,8],intervalsourc:[4,6,9,13],introduct:5,invalid:[4,6],invalidhistoryrespons:[1,2],invari:1,invok:[0,5],ipmi:12,iso:[4,14],iso_str:4,issu:[1,12],iter:[2,8],its:[0,4,6,7,11,12],itself:1,javascriptsnakecas:0,json:[7,12,14],just:11,kebab:7,keep:[6,11],kei:[0,6,7,14],keyerror:1,keyword:6,kib:14,kind:12,know:[4,10,11],known:14,kwarg:[0,2,5,6,11,12],last:[2,9,13,14],last_valu:2,latenc:6,later:4,legaci:2,less:12,let:11,level:12,levelnam:[11,12],liabil:[11,12],liabl:[11,12],librari:[1,12,13],lift:12,like:[2,4,7,11,12],limit:[0,8,10,11,12],line:[11,12],list:[0,2,5,10,11,12],lmg670:8,load:6,local:4,local_offset:10,localhost:[11,12],log:[11,12],logger:[11,12],longer:[2,6,8],lookup:[8,9,13],loss:[11,12],low:12,made:6,mai:[6,7,11,12,14],main:6,make:[2,11,12,14],manag:[0,7,14],management_url:[11,12],mani:7,manual:6,map:[0,6,10],mark:4,match:[0,2,4,10],materi:[11,12],max_interv:2,maximum:[0,2,4,8],mean:[2,6,14],measur:[5,6,7,12,14],measurand:7,memori:12,merchant:[11,12],messag:[1,11,12,14],messageerror:[1,2],met:[11,12],metadata:[0,5,6,7,9,10,12,13],method:[0,2,4,5,6,10,11,12],metric:[0,2,4,5,6,7,9,11,12,13],metricq:[0,1,2,4,5,6,7,8,9,14],metricq_sink:11,metricq_sourc:12,metricsenderror:12,microsecond:4,might:[2,14],million:8,millisecond:4,min:4,minim:12,minimum:[2,4,8],minut:[4,6,8],miscellan:[3,13],miss:6,misus:1,mode:2,modif:[11,12],modul:[1,13],monitor:[11,12,14],monoton:[1,2,4],more:[7,8,10,12],most:[2,7,8],much:6,multipl:[2,6,7,9,11,13],must:[6,7,11,12],mysourc:[4,6],name:[0,2,4,5,6,7,10,11,12,14],nanosecond:4,necessari:[7,14],need:[5,8,10,11,12,14],neg:4,neglig:[11,12],neither:[6,11,12],network:[0,1,2,5,6,7,9,10,11,12,13,14],next:[6,14],night:4,non:[2,4,6,10],none:[0,2,5,6,12],nonmonotonicerror:2,nonmonotonictimestamp:[1,4],nor:[6,11,12],note:8,notic:[11,12],now:[4,6,8,11,12],number:[0,4,6,8,12,14],numer:11,object:4,obtain:[8,11,12],occur:0,off:6,offend:0,offset:4,omit:[2,8,14],on_config:[4,6],on_data:[5,11],on_sign:0,onc:[6,11,12],one:[2,4,6,7,14],ones:2,onli:[0,1,2,4,8,12],onlin:7,onward:2,oper:[2,3,4,13],optim:7,option:[0,2,5,6,7,11,12],order:[2,4,7],org:8,other:[0,1,4,7,11,12],otherwis:[0,6,10,11,12],our:[8,11,12],out:[1,11,12],output:11,over:[2,4,7,8,12],overhead:6,overrid:[0,5,6,11,12],overriden:6,overview:8,overwritten:14,own:[7,8],owner:[11,12],packag:10,packet:6,page:[11,13],pair:[2,3,7,13,14],paramet:[0,2,4,5,6],pars:4,part:0,particular:[6,11,12],pass:[0,2,8,10,11,12],past:[4,8],pattern:[0,2],pcre:10,per:[6,12,14],perfectli:14,perform:7,period:[4,6,8,12],permiss:[11,12],permit:[11,12],persist:11,pick:6,pip:[11,12,13],place:11,plain:[10,12],point:[2,4,5,6,7,8,11,12,14],posit:6,posix:4,posix_m:4,posix_n:4,posix_u:4,possibl:[4,11,12],power:[8,10,14],precis:4,precise_str:[4,8],prefix:[0,7,9,13,14],prevent:4,print:[4,8,10,11,12],prior:[11,12],probabl:1,process:11,procur:[11,12],produc:[4,6,7,14],product:[11,12],profit:[11,12],program:12,promot:[11,12],properti:7,proto:2,protocol:[11,12],provid:[2,6,7,8,10,11,12],publish:[0,1],publisherror:0,publishfail:[1,6],pull:12,purpos:[11,12],put:6,pypi:13,python3:[11,12],python:12,quantiti:[12,14],queri:8,queue:5,quick:7,quit:12,rack:14,rad:14,rais:[0,2,4,6,12],randint:6,random:[6,12],randomli:5,rang:8,rate:[6,8,9,13,14],raw:[2,9,13],raw_tv:8,read:[6,12],readabl:[4,14],readi:8,receiv:[0,1,4,5,6,7,11,12],receivedsign:1,recent:2,recommend:[7,12],reconnect:1,reconnecttimeout:1,record:2,redistribut:[11,12],reduc:6,refer:[4,13],regex:[0,9,13],regist:2,regular:6,rel:4,relat:[4,7,12,14],relev:6,remain:[2,6],remot:[0,1],remoteerror:1,replac:12,repli:1,repo:[11,12],represent:4,reproduc:[11,12],republ:[11,12],request:[1,2,7,11],request_dur:2,request_typ:2,requir:[0,7,11,12],rerais:0,reserv:[11,12,13],respect:14,respons:[0,1,2,5,6,7],restart:[6,12],restrict:14,result:[0,4,6,8,10],retain:[11,12],retriev:[0,2,8,10],rfc:7,right:[6,11,12],room:[7,14],rough:8,round:4,routing_kei:0,rpc:[0,1,3,5,7,12,13],rpc_handler:[4,6,12],rpcerror:[0,1],run:[0,6,9,13],run_history_cli:8,run_until_complet:8,same:[4,5,6,7,11,14],sampl:14,sata:10,save:[8,12],scale:4,schedul:0,scope:[8,14],script:11,search:[9,13],second:[0,2,4,5,6,12,14],section:7,see:[0,2,4,5,6,7,8,10,11,12,14],segment:14,select:2,selector:[0,2,10],self:[4,6,11,12],semant:1,send:[2,6,12,14],sensor:12,sent:[6,7,11,12,14],separ:10,sequenc:[0,2],seri:7,server:[8,11,12],servic:[11,12],set:[0,2,6,7,11,12,14],setlevel:[11,12],setup:12,sever:7,shall:[7,11,12],share:11,shorter:4,should:[2,4,6,7,11,14],shown:14,side:1,sigint:0,signal:[0,1],sigterm:0,similarli:12,simpl:[11,12],simple_verbosity_opt:[11,12],simpli:12,sinc:[4,8],singl:[2,7,14],sink:[0,3,4,7,8,9,12,13],situat:12,size:14,skip:6,sleep:[6,12],softwar:[11,12],some:[4,6,8,12,14],some_arbitrary_metadata:6,some_sensor:6,somesensorsourc:6,someth:[1,11],sometim:7,sourc:[0,1,3,4,7,8,9,11,13,14],space:7,span:[2,4,8],special:[11,12,14],specif:[1,7,8,11,12],specifi:[2,4,6],src:12,standard:[4,11,13],start:[0,2,4,6,10,12,14],start_tim:[2,8],staticmethod:4,step:2,still:8,stop:[0,1],storag:[11,14],store:[11,14],str:[0,2,4,5,6,11],strategi:10,stream:7,strict:[11,12],strictli:[1,2,4,7],string:[4,6,7,10,12,14],strongli:12,strptime:4,style:[10,11],subclass:[5,11,12],subscrib:[5,11],substitut:[11,12],success:8,suffix:7,sum:[4,8,10],summar:[9,13],summari:4,superclass:11,suppli:[4,12],support:[4,8,10],suppos:7,sure:[2,11,12],surpris:4,symbol:14,sysinfo:[7,12],system:[7,12],take:6,task:[6,7,12],technisch:[11,12],tell:[11,12],temperatur:[6,7,14],tempor:14,term:11,test:[11,12],than:[2,4,6],thei:[1,6,7,11,12],them:[6,8],theori:[11,12],theses:0,thi:[0,1,2,4,5,6,7,8,10,11,12,13,14],those:10,though:[11,14],through:8,time:[1,2,3,5,6,7,8,11,12,13,14],timeaggreg:[2,4,8],timedelta:[2,3,6,8,13],timelin:2,timeout:[0,2],timepoint:[5,6],timespan:2,timestamp:[1,2,3,5,6,8,11,12,13],timestamp_befor:4,timevalu:[2,4,8],timezon:4,togeth:[2,4],token:[5,7,8,11,12,14],too:6,tool:14,tort:[11,12],total:4,total_ord:4,track:11,trade:6,transpar:2,treat:14,tri:12,trigger:[6,12],truncat:4,turn:6,two:[4,7,11],type:[0,2,4,5,6,7,11],typeerror:[1,6],typic:14,underl:2,underli:2,unexpectedli:[0,1],unhandl:0,union:[0,2,5],uniqu:[7,11,12],unit:[4,6,8,12,14],universitaet:[11,12],unix:4,unless:2,unpack:4,unsent:6,unspecifi:2,until:[6,8,11],updat:[6,12,14],url:[8,12],usag:12,use:[6,8,11,12,13,14],used:[1,11,12,14],useful:[5,8,10,12,14],user:[5,6,8],uses:8,using:[4,6,7,9,13],usr:[11,12],usual:12,utc:4,util:[7,12],uuid:[5,7],valid:[7,14],valu:[2,3,5,6,7,9,11,12,13,14],valueerror:[1,2,4,6],vari:14,version:[4,7],via:[0,12],visual:11,voltag:[10,14],wai:[8,11,12,14],wait:0,want:[4,6,8,10,12],warranti:[11,12],web:7,websocket:7,well:8,went:8,were:0,what:11,when:[0,4,14],where:[4,7,8,12,14],whether:[2,4,5,11,12,14],which:[2,5,6,8,11,12,14],whole:4,whose:10,within:[1,2,4],without:[6,8,11,12],wizard:12,won:[8,11,12],word:7,work:[10,12],worri:[6,11],would:[4,12,14],wouldn:12,wrap:8,written:[7,11,12],wrong:[1,2],year:8,yet:10,yield:[1,2,4],you:[0,4,6,8,10,11],your:[6,7],zero:6,zih:[11,12],zzz:10},titles:["Common client operation","Exceptions","History Client","API Reference","Miscellaneous","Sink","Source","Glossary","Fetching historical metric data","How to use this library","Metric lookup","Building a MetricQ Sink","Building a MetricQ Source","Welcome to MetricQ\u2019s documentation!","Metric Metadata"],titleterms:{"new":[11,12],aggreg:[4,8],api:3,build:[11,12],client:[0,2],common:0,complet:[11,12],connect:8,constant:12,data:8,defin:[11,12],document:13,durat:4,exampl:[11,12],except:1,fetch:8,field:14,get:8,glossari:7,handl:4,histor:8,histori:2,how:9,improv:12,indic:13,infix:10,instal:13,intervalsourc:12,last:8,librari:9,lookup:10,metadata:[8,14],metric:[8,10,14],metricq:[11,12,13],miscellan:4,multipl:8,network:8,oper:0,pair:4,prefix:10,quickstart:13,rate:12,raw:8,refer:3,regex:10,reserv:14,rpc:4,run:[11,12],search:10,sink:[5,11],sourc:[6,12],standard:14,summar:8,tabl:13,thi:9,time:4,timedelta:4,timestamp:4,use:9,using:[11,12],valu:[4,8],welcom:13}})