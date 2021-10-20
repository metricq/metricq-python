Search.setIndex({docnames:["api/client-common","api/drain","api/exceptions","api/history-client","api/index","api/misc","api/sink","api/source","api/subscriber","glossary","howto/drain","howto/history-client","howto/index","howto/metric-lookup","howto/project-structure","howto/sink","howto/source","index","metadata","upgrading"],envversion:{"scanpydoc.definition_list_typed_field":1,"scanpydoc.elegant_typehints":1,"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,sphinx:56},filenames:["api/client-common.rst","api/drain.rst","api/exceptions.rst","api/history-client.rst","api/index.rst","api/misc.rst","api/sink.rst","api/source.rst","api/subscriber.rst","glossary.rst","howto/drain.rst","howto/history-client.rst","howto/index.rst","howto/metric-lookup.rst","howto/project-structure.rst","howto/sink.rst","howto/source.rst","index.rst","metadata.rst","upgrading.rst"],objects:{"metricq.Agent":{rpc:[0,0,1,""]},"metricq.Client":{connect:[0,0,1,""],get_metrics:[0,0,1,""],on_signal:[0,0,1,""],rpc:[0,0,1,""],run:[0,0,1,""],stop:[0,0,1,""],stopped:[0,0,1,""]},"metricq.Drain":{__aenter__:[1,0,1,""],__aiter__:[1,0,1,""],__init__:[1,0,1,""],connect:[1,0,1,""]},"metricq.HistoryClient":{connect:[3,0,1,""],get_metrics:[3,0,1,""],history_aggregate:[3,0,1,""],history_aggregate_timeline:[3,0,1,""],history_data_request:[3,0,1,""],history_last_value:[3,0,1,""],history_raw_timeline:[3,0,1,""]},"metricq.IntervalSource":{period:[7,0,1,""],update:[7,0,1,""]},"metricq.Sink":{connect:[6,0,1,""],on_data:[6,0,1,""],subscribe:[6,0,1,""]},"metricq.Source":{chunk_size:[7,2,1,""],connect:[7,0,1,""],declare_metrics:[7,0,1,""],flush:[7,0,1,""],send:[7,0,1,""],task:[7,0,1,""]},"metricq.Subscriber":{__init__:[8,0,1,""],connect:[8,0,1,""],drain:[8,0,1,""],queue:[8,2,1,""]},"metricq.TimeAggregate":{active_time:[5,2,1,""],count:[5,2,1,""],from_value_pair:[5,0,1,""],integral_ns:[5,2,1,""],integral_s:[5,0,1,""],maximum:[5,2,1,""],minimum:[5,2,1,""],sum:[5,2,1,""],timestamp:[5,2,1,""]},"metricq.TimeValue":{timestamp:[5,2,1,""],value:[5,2,1,""]},"metricq.Timedelta":{__floordiv__:[5,0,1,""],__mul__:[5,0,1,""],__str__:[5,0,1,""],__truediv__:[5,0,1,""],from_ms:[5,0,1,""],from_s:[5,0,1,""],from_string:[5,0,1,""],from_timedelta:[5,0,1,""],from_us:[5,0,1,""],ms:[5,0,1,""],ns:[5,0,1,""],s:[5,0,1,""],timedelta:[5,0,1,""],us:[5,0,1,""]},"metricq.Timestamp":{__add__:[5,0,1,""],__eq__:[5,0,1,""],__lt__:[5,0,1,""],__str__:[5,0,1,""],ago:[5,0,1,""],datetime:[5,0,1,""],from_datetime:[5,0,1,""],from_iso8601:[5,0,1,""],from_now:[5,0,1,""],from_posix_seconds:[5,0,1,""],now:[5,0,1,""],posix:[5,0,1,""],posix_ms:[5,0,1,""],posix_ns:[5,0,1,""],posix_us:[5,0,1,""]},"metricq.exceptions":{AgentStopped:[2,4,1,""],ConnectFailed:[2,4,1,""],HistoryError:[2,4,1,""],InvalidHistoryResponse:[2,4,1,""],MessageError:[2,4,1,""],NonMonotonicTimestamps:[2,4,1,""],PublishFailed:[2,4,1,""],RPCError:[2,4,1,""],ReceivedSignal:[2,4,1,""],ReconnectTimeout:[2,4,1,""],RemoteError:[2,4,1,""]},"metricq.history_client":{HistoryRequestType:[3,1,1,""],HistoryResponse:[3,1,1,""],HistoryResponseType:[3,1,1,""],InvalidHistoryResponse:[3,1,1,""]},"metricq.history_client.HistoryRequestType":{AGGREGATE:[3,2,1,""],AGGREGATE_TIMELINE:[3,2,1,""],FLEX_TIMELINE:[3,2,1,""],LAST_VALUE:[3,2,1,""]},"metricq.history_client.HistoryResponse":{aggregates:[3,0,1,""],mode:[3,0,1,""],values:[3,0,1,""]},"metricq.history_client.HistoryResponseType":{AGGREGATES:[3,2,1,""],EMPTY:[3,2,1,""],LEGACY:[3,2,1,""],VALUES:[3,2,1,""]},metricq:{Client:[0,1,1,""],Drain:[1,1,1,""],HistoryClient:[3,1,1,""],IntervalSource:[7,1,1,""],Sink:[6,1,1,""],Source:[7,1,1,""],Subscriber:[8,1,1,""],TimeAggregate:[5,1,1,""],TimeValue:[5,1,1,""],Timedelta:[5,1,1,""],Timestamp:[5,1,1,""],exceptions:[2,3,0,"-"],rpc_handler:[5,5,1,""]}},objnames:{"0":["py","method","Python method"],"1":["py","class","Python class"],"2":["py","attribute","Python attribute"],"3":["py","module","Python module"],"4":["py","exception","Python exception"],"5":["py","decorator","decorator"]},objtypes:{"0":"py:method","1":"py:class","2":"py:attribute","3":"py:module","4":"py:exception","5":"py:decorator"},terms:{"012270469843231":11,"013008404218427":11,"016890013553053":11,"018666244768894":11,"01t00":[5,11],"021740922113744":11,"022798681983203":11,"029395457601895":11,"0298144051392155":11,"02t02":11,"037842717663995":11,"0443300790978025":11,"045782289231323":11,"0495328431393665":11,"052929845492045":11,"055744129198569":11,"059901887791767":11,"06578061778873023":15,"070213303973638":11,"070445673918661":11,"074948972951139":11,"085156064549348":11,"0869138":11,"08725953086385":11,"090598201216997":11,"092209875269113":11,"09505560184217":11,"09832763671875":11,"100":[7,11],"1000":7,"1000000000000000":11,"100hz":13,"100m":11,"103712609":11,"105834719":11,"109231486484054":11,"109705217910005":11,"109750890322914":11,"10min":11,"113817063":11,"11998":11,"1266322950":11,"12v":13,"137031078338623":11,"140197859":11,"1490083450372932":15,"154049873352051":11,"1576000000000000000":11,"1577000000000000000":11,"1577836799998195277":11,"1577836800008200879":11,"1577836800018206481":11,"1577836800028212083":11,"1577836800038217685":11,"1577836800048223287":11,"1577836800058228890":11,"1577836800068234492":11,"1577836800078240094":11,"1577836800088245696":11,"1577836800098251298":11,"1578000000000000000":11,"1579000000000000000":11,"1580000000000000000":11,"1581000000000000000":11,"1582000000000000000":11,"1583000000000000000":11,"1584000000000000000":11,"1585000000000000000":11,"1586000000000000000":11,"1587000000000000000":11,"1588000000000000000":11,"1588509320269324000":15,"1588509321269232000":15,"1588509322269017000":15,"1588509323267878000":15,"1588509324267969000":15,"1589000000000000000":11,"1590000000000000000":11,"1591000000000000000":11,"1592000000000000000":11,"1593000000000000000":11,"1594000000000000000":11,"1595000000000000000":11,"1596000000000000000":11,"1597000000000000000":11,"1598000000000000000":11,"1599000000000000000":11,"1600000000000000000":11,"1601000000000000000":11,"1602000000000000000":11,"1603000000000000000":11,"1604000000000000000":11,"1605000000000000000":11,"1606000000000000000":11,"1607604944653649318":11,"1607605522779676000":11,"1678637":11,"16907605898412":11,"181990750389552":11,"183813638":11,"186786145522286":11,"189763454302634":11,"189800217157934":11,"1970":5,"198339989443255":11,"19898286":11,"19941570890925":11,"19998732":11,"19998746":11,"19998790":11,"19998832":11,"1hz":13,"2018":16,"2019":15,"2020":[11,15],"20e76d0b06769485e428d866a40a19e9":11,"20s":[15,16],"2119":9,"2123122215271":11,"21305943793546":11,"226152306810846":11,"22672075":11,"255":[0,3],"260790772048024":11,"267878":15,"267969":15,"269017":15,"269232":15,"2692437313689422e":11,"269324":15,"2714809":11,"27197903394699097":11,"275346755981445":11,"2770119258139":11,"28786822296384":11,"2884533":11,"29484596848487854":11,"29932484337397":11,"30919786870951":11,"30d":11,"314934986":11,"317270364484564":11,"325960":11,"33296203613281":11,"333333333":5,"3333333333n":5,"336227685213089":11,"3441083":11,"356d":11,"36389875":11,"365":11,"371744397447735":11,"40338314":11,"4122":9,"4169525":11,"4198bdddab794e9f8d774a590651cdc1":9,"421671555":11,"421677696":11,"422114944":11,"4227204663817987":11,"422796585":11,"4230758481433696":11,"4232455502722522":11,"4236512307816254":11,"425685373":11,"42605497043147944":11,"4270007113356799":11,"428285008":11,"428877311":11,"4291822388062562":11,"4297132066602203":11,"430180936":11,"4310744175027674":11,"440":14,"449131406548784":11,"451322892":11,"4525474207319798":11,"456466462178092":11,"462386484":11,"46617925":11,"46623087":11,"466414451599121":11,"4685728":11,"47610932352675":11,"477295609":11,"4783373487851792":11,"48311378740654076":15,"489314953":11,"4905119547247363":11,"49095530623182":11,"496343":11,"497292058134455":11,"4973650909724805":11,"500":19,"500m":19,"501395874728":11,"504241073":11,"5051357041124994":11,"5058164":11,"50840513687335":11,"512623432":11,"513875664":11,"5140939976375570":11,"5148844813659733":11,"517":14,"5185936811198162":11,"522117803":11,"5292031471206438":11,"5332946931093845":11,"53575706482":11,"5427221":11,"54902472030519":11,"55397":11,"555991185":11,"5588739148089780":11,"56394789":11,"566789400":11,"5680943171485073":11,"5691203189059035":11,"5692853013069647":11,"577018180":11,"577035544":11,"577227484":11,"577390774":11,"5781975868653922":11,"5788576471647640":11,"5792219436779407":11,"5794758614134834":11,"58503866":11,"593994374":11,"5998410892025108":11,"599930363353":11,"5b1":14,"600963661727302":11,"6042662":11,"604800000000000":5,"6053987":11,"61448812":11,"6226":11,"624169682":11,"62433964":11,"646619296011":11,"6533275":11,"653649":11,"6805707983731595":11,"681345060035232":11,"68548583984375":11,"7010239213612438":11,"71097277085196":11,"71681815":11,"7307683":11,"734305978764959":11,"73528534":11,"7391233":11,"750031412119604":11,"77031535":11,"7771949055949513":15,"779":11,"7939971":11,"82585525512695":11,"848274261152525":11,"855274849":11,"8586157900774826":11,"8599746":11,"8601":[5,18],"86400":5,"8778002158455225":11,"88969261":11,"8951057":11,"9000":9,"9020380477110543":11,"903405893044394":11,"92287374":11,"9249958538284772":11,"93735992":11,"9538565":11,"97846984863281":11,"9841194152832":11,"98658756":11,"991440138904906":11,"99468962":11,"99503304":11,"99565403":11,"99625754":11,"99692006":11,"99702528":11,"99704757":11,"99734524":11,"99748050":11,"99751312":11,"9975132302199418":15,"99759123":11,"99769118":11,"99777911":11,"99790000":11,"99790197":11,"99793322":11,"99795005":11,"99797773":11,"99802606":11,"99804732":11,"99806981":11,"99840737":11,"break":[14,19],"byte":[0,3],"case":[0,3,7,9,10],"catch":3,"class":[0,1,2,3,5,6,7,8,10,14,15,16,17],"default":[0,3,6,14,15,16],"final":[14,16],"float":[0,3,5,6,7,8,15],"function":[0,14],"import":[5,7,10,11,14,15,16,19],"int":[0,5,6,7,8],"long":[5,11,14],"new":[3,6,7,10,12,17,18,19],"null":18,"public":0,"return":[0,1,2,3,5,6,7,8,11,13,14,16,19],"short":5,"static":14,"super":[7,14,15,16],"true":[0,3,5,6,7,11,13,14,15,16,19],"while":[7,10,16],AND:[15,16],ARE:[15,16],BUT:[15,16],FOR:[15,16],For:[9,10,14,15,16,18],NOT:[9,15,16],One:5,SUCH:[15,16],THE:[15,16],TLS:19,That:18,The:[0,1,2,3,5,7,8,9,10,13,14,15,16,18,19],Then:[11,14],There:[2,7],These:[9,19],USE:[15,16],Use:[0,1,3,5,7,9,11,14],Using:11,__add__:5,__aenter__:1,__aiter__:1,__eq__:5,__floordiv__:5,__init__:[1,7,8,14,15,16],__lt__:5,__main__:[15,16],__mul__:5,__name__:[15,16],__str__:5,__truediv__:5,__version__:14,_config:7,_id:[11,18],_metric:15,_on_config:[7,16],_rate:16,_rev:11,a_week_lat:5,abc:13,about:[7,11,15],abov:[10,14,15,16],absolut:14,abstractmethod:[6,7],accept:[5,19],access:[3,14],accident:[14,19],accord:[9,18],accordingli:11,activ:[5,14],active_tim:[5,11,19],adapt:16,add:[14,15],add_uuid:[6,15],added:[3,14,19],addit:[0,5,9,14],advis:[7,15,16],affect:7,after:[0,3,7,8,10,15],again:[7,8,10],age:11,agent:[0,2,19],agentstop:[0,2,19],agentstoppederror:19,agg:19,aggreg:[3,4,12,17],aggregate_timelin:3,ago:[5,11],all:[0,1,3,5,7,10,11,13,14,15,16,18,19],allow:[0,1,14,15],almost:[7,11],alreadi:[5,13],also:14,altern:[3,13],alwai:[2,13],ambigu:17,amqp:[10,11,14,15,16],ani:[0,3,5,6,7,9,10,14,15,16,18],anoth:[5,14,16],anyth:[16,19],apart:3,api:[0,2,13,17],appear:15,append:[6,9],appli:[13,18],applic:[7,9,14],approach:10,appropri:[14,16,18,19],approv:14,arbitrari:[7,9,18],arg:[0,1,2,3,6,7,8,14,15,16],argument:[0,3,5,7,13,14,15],ariel:[11,13],aris:[15,16],arriv:[0,6,15],asctim:[15,16],ask:14,assert:[2,5,14],assertionerror:2,assign:[7,19],associ:[11,18],assum:[14,15],async:[1,5,7,8,10,11,14,15,16],asynchron:[1,15],asyncio:[7,10,11,14,16],attach:[0,2,9],attempt:[2,7],attribut:19,author:14,autom:16,automat:[1,7,10,14,15,16,19],avail:[9,13,19],averag:[3,11],await:[0,1,3,6,7,8,11,13,15,16,19],awar:[5,7],b950:14,backend:[14,18],bacnet:16,bahavior:10,bandwidth:11,bar:[7,14],base:[0,3,5,6,11,14,15,19],basic:14,basic_config:[15,16],been:[15,19],befor:[3,5,7,8,9,14],behav:[5,11],behavior:3,behaviour:7,being:[7,14,18],below:[0,3,11,16,19],best:18,better:14,between:[3,7,14,16,18],bin:[15,16],binari:[14,15,16],black:14,block:15,board:13,bool:[0,3,5,6,18],both:[3,10,11],breakag:14,bright_blu:15,broken:19,bsd:14,buffer:[1,7,8,12,17],bugbear:14,build:[6,7,9,11,12,17],build_meta:14,built:[2,14,16],busi:[15,16],calcul:11,call:[0,3,5,7,8,9,13,14,15,16],callabl:[0,5],callback:[0,6,15,16],can:[7,10,11,14,15,16,18],cancel_on_except:0,cannot:[7,14],care:7,catch_sign:0,caught:7,caus:[0,2,10,14,15,16,19],certain:5,cfg:14,chang:[7,16,17],check:[2,5,14],choos:14,chronolog:9,chunk:[7,17,18],chunk_offset:13,chunk_siz:[7,18,19],chunksiz:18,citizen:14,classifi:14,classmethod:5,claus:14,cleanli:3,cleanup_on_respons:0,cli:14,click:[14,15,16],click_complet:[15,16],click_log:[15,16],client:[4,5,6,9,10,11,13,14,15,16,17,19],client_token:14,client_vers:[0,14],close:[1,8,10,15],code:[2,7,10,11,14,15,16,19],collect:[7,10],com:14,combin:5,command:[12,15,16,17],commit:14,common:[4,16,17],commun:16,compar:[5,11],compat:14,compens:16,compil:14,complet:[12,17],compliant:14,complic:[11,16],compon:13,concret:9,condit:[15,16],config:[5,7,14,16],configur:[5,7,8,14,16],conflict:14,confus:[14,19],connect:[0,1,2,3,6,7,8,9,10,12,15,16,17,19],connectfail:[0,2,19],connectfailederror:19,consecut:[3,7,16],consequenti:[15,16],consist:14,console_script:14,constant:[7,12,17,18],construct:[15,16],constructor:[14,15],consum:[9,10,18],consumpt:9,contain:[0,1,3,5,11,13,14,15,16,19],content:14,context:[1,3,8,10],contin:10,continu:16,contract:[15,16],contrari:2,contrast:10,contributor:[15,16],control:7,conveni:[5,16],convent:14,convert:[3,5,16],copyright:[15,16],core:9,coroutin:16,correct:5,correspond:5,could:[0,2,3,14,19],count:[5,11,18],counter:7,cours:9,cover:[3,11],cpu:[9,16],creat:[5,6,10,12,16,17],create_subprocess_exec:10,current:[10,16],custom:[0,2],cycl:11,dai:[5,11],damag:[15,16],data:[1,3,6,7,8,9,12,15,16,17,18],databas:[2,11,15,18],datapoint:15,date:[5,11,14,18],datetim:5,dateutil:5,deadlin:7,declar:[7,9,14,16,18],declare_metr:[7,16,18],decod:[2,3],decor:[5,14,16],def:[5,7,11,14,15,16],default_language_vers:14,defin:[2,6,11,12,14,17,18],delet:10,delimit:11,delta:[5,11],depend:[3,12,13,15,16,17],deprec:17,deriv:[0,15,16],describ:[5,9,18],descript:[3,7,14,16,18],design:[10,15],desir:[3,9],detail:[3,9,13,15],determin:[3,14],dev:14,develop:[12,17],dict:[0,3,6,7],dictionari:[0,7,13],diff:14,differ:[5,6,13,15,16],digit:5,dimensionless:18,direct:[15,16],directli:[11,15,19],directori:14,disabl:[7,19],disc:9,disclaim:[15,16],disconnect:8,dispatch:0,displai:[9,18],distinct:[3,9],distinguish:[6,9],distribut:[15,16],divid:5,divis:5,document:[3,9,13,15,16,19],doe:[3,10,14,16,18],drain:[4,8,12,17],dram:[11,13],dresden:[14,15,16],drop:5,dummi:[14,15,16],dummysink:15,dummysourc:16,duplic:7,durat:[3,4,11,16,17,19],duration_str:5,dynam:16,dzzze:13,e13:18,e203:14,e27:9,e501:14,each:[3,9,11,14,15,18],easi:14,easiest:10,echo:15,edit:14,effect:5,either:[0,2,3,7,11,14,18],elab:[11,13],elaps:5,elif:3,els:3,empti:[3,16,18],enabl:14,encount:0,encrypt:19,end:15,end_tim:[3,11],endors:[15,16],enforc:14,ensur:9,enter:[14,16],entri:[11,14],entry_point:14,env:[15,16],environ:14,epoch:5,equival:5,error:[0,2,5,16,19],establish:[1,10,15],estim:18,etc:[0,3,5,9,11,14],even:[7,10,15,16],event:[15,16],everi:[6,7,15,16],evolv:9,exactli:13,exampl:[5,7,9,10,11,12,14,17,18],except:[0,3,4,7,16,17],exchang:[0,2,9],exclud:14,execut:[7,14],exemplari:[15,16],exhaust:3,exist:13,expect:[5,18],expens:11,experi:14,expir:[6,8,10],explain:14,explicitli:14,explor:11,express:[15,16],extend:14,extens:14,extra:[14,15,16],extra_messag:[2,3],extras_requir:14,factor:5,fail:[0,2,3,7,19],failur:7,fals:[0,3,5,13],fan:13,far:16,featur:14,feder:[15,16],fetch:[3,10,12,17],fgh:13,field:[9,17],file:14,filesystem:14,filter:0,find:15,finish:8,first:[0,3,7,10,11,15,16],fit:[15,16],fix:16,flag:0,flake8:14,flex_timelin:3,floor:5,flush:7,fmt:[15,16],follow:[0,9,10,14,15,16,19],foo:[7,14],forget:14,form:[5,15,16,18],format:[3,5,9,14,15,16,18],formatt:[14,15,16],forward:[0,15],free:[9,18],from:[0,3,5,7,10,14,15,16,19],from_:[5,7],from_datetim:5,from_iso8601:[5,11],from_m:[5,19],from_now:5,from_posix_second:5,from_str:[5,11],from_timedelta:5,from_u:5,from_value_pair:[5,19],frontend:[9,16],fulli:8,function_tag:5,functool:5,further:5,futur:[3,5,14],gave:19,gener:[2,6,7,15,18,19],germani:[15,16],get:[1,7,10,12,15,16,17],get_logg:[15,16],get_metr:[0,3,11,13,19],get_some_sensor_valu:7,git:[14,15,16],github:14,gitignor:14,gitlab:14,give:[14,18],given:[0,1,7,8,10,13,15],glossari:17,good:[9,14,15,16],guess:18,had:[15,19],hal:9,hand:[3,14],handl:[0,3,4,6,7,10,15,16,17,18,19],handler:[0,5,15,16],happen:5,harder:19,has:[2,3,5,7,8,14,15,19],have:[5,7,9,10,11,14,18,19],heavi:16,hello:14,help:[14,16],henc:5,here:[3,10,11,14,15,16,19],hex:9,hidden:0,higher:5,hint:18,histor:[0,3,12,13,17,18],histori:[2,4,11,17],history_aggreg:[3,11],history_aggregate_timelin:[3,11],history_cli:[3,19],history_data_request:3,history_last_valu:[3,11],history_metric_list:19,history_metric_metadata:19,history_raw_timelin:[3,11],historycli:[0,3,5,11,14,19],historyerror:2,historyrequesttyp:3,historyrespons:3,historyresponsetyp:3,hold:15,holder:[15,16],hook:14,hopefulli:14,host:[9,14],hour:[5,11],how:[0,3,6,7,9,11,15,17],howev:[15,16],hta:15,http:14,human:[5,18],hurt:14,idea:11,ideal:18,identif:16,identifi:[9,11,14,15],ignor:[14,15,16],immedi:[0,7],implement:[5,6,7,9,10,15,16,18],impli:[15,16],importerror:19,improv:[12,17],incident:[15,16],includ:[0,3,14,15,16,18],inclus:3,incom:[6,10],incompat:14,increas:3,increment:7,index:17,indic:[15,16,18],indirect:[15,16],individu:7,inevit:16,infer:14,infix:[0,12,17],info:[9,15,16],inform:[0,3,9,11,14,16,18],inherit:0,init:[10,15,16],initi:[7,10,15,16],input:2,instal:[12,15,16],install_requir:14,instanc:[5,6,8,9,10,11,15,19],instead:[0,7,11,15,16,19],instruct:17,integ:[5,7,19],integr:[5,11,17],integral_:[5,19],integral_n:[5,19],intend:6,interact:2,interest:[3,11,15],interfac:[12,13,15,17],interpret:[3,9],interrupt:[15,16],interv:[7,16],interval_max:[3,11],intervalsourc:[5,7,12,17,19],introduc:14,introduct:6,invalid:[5,7],invalidhistoryrespons:[2,3,19],invari:2,invok:[0,6],ipmi:16,iso:[5,18],iso_str:5,isopars:5,isort:14,issu:[2,14,16,19],iter:[0,1,3,10,11],its:[0,5,7,9,14,15,16],itself:[0,2,14],javascriptsnakecas:0,json:[9,16,18],just:15,kebab:9,keep:[7,14,15],kei:[0,7,9,18],keyerror:2,keyword:[0,7],kib:18,kind:16,know:[5,13,15],known:18,kwarg:[0,1,3,6,7,8,15,16],languag:14,last:[3,12,17,18],last_valu:3,latenc:7,later:[5,7],least:14,legaci:3,length:14,less:[14,16],let:15,level:16,levelnam:[15,16],liabil:[15,16],liabl:[15,16],librari:[2,14,16,17],licens:14,license_fil:14,lifetim:8,lift:16,like:[1,3,5,9,10,14,15,16],limit:[0,11,13,15,16],line:[12,15,16,17],linter:14,list:[1,3,6,8,10,13,14,15,16,19],live:[10,14],lmg670:11,load:7,local:[5,14],local_offset:13,localhost:[14,15,16],locat:17,log:[15,16],logger:[15,16],long_descript:14,long_description_content_typ:14,longer:[0,3,7,11],lookup:[11,12,17],loss:[15,16],low:16,made:7,magic:14,mai:[7,9,10,15,16,18],main:[7,14],mainten:14,major:19,make:[3,14,15,16,18,19],manag:[0,1,8,9,10,18],management_url:[15,16],managementrpcpublisherror:19,mani:[9,14],manifest:14,manual:7,map:[0,7,13],mark:5,markdown:14,match:[0,3,13,19],materi:[15,16],max:14,max_interv:3,maximum:[0,3,5,11],mean:[3,7,18],measur:[6,7,9,10,16,18],measurand:9,memori:16,merchant:[15,16],merg:14,messag:[2,15,16,18],messageerror:[2,3],met:[15,16],metadata:[0,6,7,9,12,13,16,17,19],metavar:14,method:[0,3,5,6,7,13,15,16,17],metric:[0,1,3,5,6,7,8,9,12,15,16,17],metricq:[0,1,2,3,5,6,7,8,9,11,12,18],metricq_exampl:14,metricq_sink:15,metricq_sourc:16,metricsenderror:19,mgedmin:14,microsecond:5,might:[3,18,19],million:11,millisecond:5,min:5,minim:16,minimum:[3,5,11,14,19],minut:[5,7,11],miscellan:[4,17],miss:[0,7],misus:[2,19],mode:3,modif:[15,16],modul:[2,14,17,19],monitor:[15,16,18],monoton:[2,3,5],more:[9,11,13,14,16,19],most:[0,3,9,10,11],move:19,much:[7,10],multipl:[3,7,9,12,15,17],must:[0,7,8,9,14,15,16],my_drain:1,my_featur:14,mysourc:[5,7,14],name:[0,1,3,5,6,7,8,9,13,14,15,16,18],nanosecond:[5,19],necessari:[9,14,18],need:[5,6,7,11,13,14,15,16,18],neg:5,neglig:[15,16],neither:[7,15,16],network:[0,1,2,3,6,7,8,9,12,13,14,15,16,17,18],never:10,newer:17,next:[7,18],night:5,non:[3,5,7,13],none:[0,1,3,5,6,7,8,15,16,19],nonmonotonictimestamp:[2,3,5],nor:[7,15,16],normal:10,note:[11,14],notic:[15,16],now:[5,7,10,11,15,16,19],number:[0,5,7,11,16,18,19],numer:15,object:[5,10],obtain:[11,15,16],occur:0,off:7,offend:0,offset:5,older:14,omit:[0,3,11,18],on_config:[5,7],on_data:[6,15],on_sign:0,onc:[0,7,10,15,16],one:[3,5,7,9,18],ones:3,onli:[0,2,3,5,8,10,11,14,16,19],onlin:9,onward:3,open:10,oper:[3,4,5,14,17],optim:9,option:[0,3,5,6,7,8,9,15,16],order:[3,5,9,14],org:[10,11],osi:14,other:[0,2,5,9,10,14,15,16,19],otherwis:[0,7,13,14,15,16],our:[11,15,16],out:[2,15,16],output:15,outsid:14,over:[0,1,3,5,9,10,11,16,19],overhead:[7,14],overrid:[0,6,7,15,16],overriden:7,overview:11,overwrit:7,overwritten:18,own:[9,11],owner:[15,16],packag:13,packet:7,page:[15,17],pair:[3,4,9,17,18],paramet:[0,1,3,5,6,7,8,10],pars:[5,14],parser:5,part:[0,14],particluar:10,particular:[7,10,15,16],pass:[0,1,3,10,11,13,15,16],past:[5,11],path:14,pattern:[0,3],pcre:13,pep8:14,pep:14,per:[7,10,16,18],perfectli:18,perform:[8,9,10],period:[5,7,11,16,19],permiss:[15,16],permit:[15,16],persist:15,perturb:10,pick:[7,14],pip:[14,15,16,17],place:[14,15],plain:[13,16],plugin:14,point:[3,5,6,7,9,10,11,14,15,16,18],posit:[7,19],posix:5,posix_m:5,posix_n:5,posix_u:5,possibl:[5,10,14,15,16],post:10,power:[11,13,18],pre:14,precis:5,precise_str:[5,11,19],prefer:14,prefix:[0,9,12,17,18],prevent:[5,14],previous:17,print:[5,11,13,15,16],prior:[15,16],probabl:2,process:[8,10,15],procur:[15,16],produc:[5,7,9,14,18],product:[15,16],profit:[15,16],program:[10,14,16],project:[12,17],promot:[15,16],proper:19,properti:[9,19],proto:3,protobuf:14,protoc:14,protocol:[15,16],provid:[3,7,9,10,11,13,14,15,16],psf:14,publish:[0,2],publishfail:[0,2,7,16,19],publishfailederror:19,pull:[14,16],purpos:[15,16],put:7,pycqa:14,pypi:[14,17],pyproject:14,pytest:14,pytest_cach:14,python3:[14,15,16],python:[14,16,17],python_requir:14,pythonproject:14,quantiti:[16,18],queri:11,queue:[1,6,8],quick:9,quit:16,rabbitmq:0,rack:18,rad:18,rais:[0,3,5,7,16,19],randint:7,random:[7,16],randomli:6,rang:11,rate:[7,11,12,17,18],raw:[3,12,17,19],raw_tv:11,read:[7,16],readabl:[5,18],readi:11,readm:14,reason:14,receiv:[0,1,2,5,6,7,9,12,15,16,17],receivedsign:[2,19],receivedsignalerror:19,recent:3,recommend:[9,14,16],reconnect:2,reconnecttimeout:2,record:3,redistribut:[15,16],reduc:[7,10,14,17],refer:[0,5,17],regex:[0,12,17],regist:3,regular:[7,14],rel:[5,14],relat:[5,9,16,18],releas:[14,19],relev:[7,14],remain:[3,7],rememb:14,remot:[0,2],remoteerror:2,remov:17,replac:[14,16],repli:2,repo:[14,15,16],repres:10,represent:5,reproduc:[15,16],republ:[15,16],request:[0,2,3,8,9,10,14,15],request_dur:3,request_typ:3,requir:[0,9,10,14,15,16,17],rerais:0,reserv:[15,16,17],reset:7,respect:[18,19],respons:[0,2,3,6,7,9],response_callback:0,restart:[7,16],restrict:18,result:[0,5,7,8,11,13],retain:[15,16],retriev:[0,3,11,13],rev:14,revis:14,rfc:9,right:[7,10,15,16],room:[9,18],root:14,rough:11,round:5,rout:0,routing_kei:0,rpc:[0,2,4,6,8,9,16,17],rpc_handler:[5,7,16],rpcerror:[0,2,19],rpcreplyerror:19,rst:14,rule:14,run:[0,7,10,12,14,17],run_history_cli:11,run_until_complet:11,same:[5,6,7,9,14,15,18],sampl:18,sata:13,save:[11,16],scale:5,schedul:0,scheme:[14,19],scope:[11,18],script:[14,15],search:[12,17],second:[0,3,5,6,7,8,10,16,18,19],section:[9,14],see:[0,3,5,6,7,9,11,13,14,15,16,17,18],segment:18,select:[3,14],selector:[0,3,13],self:[5,7,14,15,16],semant:2,semver:[14,19],send:[3,7,8,16,18],sensibl:14,sensor:16,sent:[7,9,15,16,18],separ:13,sequenc:[0,3],seri:9,server:[10,11,14,15,16],servic:[15,16],set:[0,3,7,8,9,14,15,16,18],setlevel:[15,16],setup:[12,16,17],setuptool:14,setuptools_scm:14,sever:9,shall:[9,10,15,16],share:15,shartli:10,shorter:5,should:[3,5,7,8,9,14,15,18],show_default:14,shown:18,side:2,sigint:0,signal:[0,2],sigterm:0,similarli:16,simpl:[15,16],simple_verbosity_opt:[15,16],simpli:[5,16],sinc:[5,11],singl:[3,9,14,18],sink:[0,4,5,9,10,11,12,14,16,17,19],sinkerror:19,sinkresubscribeerror:19,situat:16,size:[17,18],skip:7,sleep:[7,16],softwar:[15,16],some:[5,7,11,14,16,18,19],some_arbitrary_metadata:7,some_sensor:7,somesensorsourc:7,someth:[2,15],sometim:9,sort:14,sourc:[0,2,4,5,9,11,12,14,15,17,18],space:9,span:[3,5,11,19],special:[10,15,16,18],specif:[2,9,11,15,16],specifi:[3,5,7,14],spend:14,src:16,ssl:19,standard:[5,15,17],start:[0,3,5,7,10,13,16,18],start_tim:[3,11],statement:[8,10,14],staticmethod:5,step:[3,19],still:11,stop:[0,2,7,10],storag:[15,18],store:[15,18],str:[0,1,3,5,6,7,8,10,14,15,16],strategi:13,stream:[9,10],strict:[15,16],strictli:[2,3,5,9],string:[5,7,9,13,14,16,18],strongli:16,style:[13,14,15],sub:5,subclass:[6,15,16],subdirectori:14,submodul:19,subscrib:[1,4,6,12,15,17],subscript:[8,10],substitut:[15,16],success:11,successfulli:8,suffix:[9,19],suggest:19,sum:[5,11,13],summar:[12,17],summari:5,superclass:15,supersed:19,suppli:[5,14,16],support:[5,7,11,13,14,19],suppos:9,sure:[3,15,16,19],surpris:5,symbol:18,sysinfo:[9,16],system:[9,16,19],tag:14,take:[7,19],task:[7,9,10,16],technisch:[15,16],tell:[14,15,16],temperatur:[7,9,18],tempor:18,term:[14,15],termin:10,test:[15,16],test_:14,test_foo:14,test_hello:14,tester:14,text:14,than:[0,3,5,7],thei:[2,7,9,14,15,16,19],them:[7,11,14,19],theori:[15,16],therefor:19,theses:0,thi:[0,1,2,3,5,6,7,8,9,10,11,13,14,15,16,17,18,19],those:13,though:[15,18],through:11,thu:19,time:[1,2,3,4,6,7,8,9,10,11,14,15,16,17,18,19],timeaggreg:[3,5,11,17],timedelta:[3,4,7,8,10,11,17,19],timelin:3,timeout:[0,3],timepoint:[6,7],timespan:3,timestamp:[2,3,4,6,7,11,15,16,17,19],timestamp_befor:5,timevalu:[3,5,11],timezon:5,timothycroslei:14,togeth:[3,5,19],token:[6,9,11,14,15,16,18],toml:14,too:[7,14],tool:[14,18],tort:[15,16],total:5,total_ord:5,track:[14,15],trade:7,transit:14,transpar:3,treat:18,tri:16,trigger:[7,16],truncat:5,truth:14,tupl:19,turn:7,two:[5,9,15],type:[0,1,3,5,6,7,8,9,14,15,16,17],typeerror:[0,2,7],typic:18,under:14,underl:3,underli:3,unexpectedli:[0,2],unhandl:0,union:[0,3,6,8],uniqu:[9,15,16],unit:[5,7,11,16,18,19],universitaet:[15,16],unix:5,unless:3,unpack:[5,19],unsent:7,unspecifi:3,until:[7,10,11,15],updat:[7,16,18],url:[11,14,16],usag:16,use:[1,7,8,10,11,14,15,16,17,18,19],used:[2,8,10,15,16,18,19],useful:[6,10,11,13,14,16,18],user:[6,7,10,11],uses:11,using:[5,7,8,9,12,14,17],usr:[15,16],usual:[14,16],utc:5,utf:0,util:[9,16],uuid:[6,9],valid:[9,17,18],valu:[1,3,4,6,7,8,9,10,12,15,16,17,18,19],valueerror:[0,2,3,5,7],vari:18,variabl:14,version:[7,9,12],version_opt:14,version_tupl:14,via:[0,16],virtual:14,visual:15,voltag:[13,18],w503:14,wai:[10,11,15,16,18],wait:0,want:[1,5,7,8,10,11,13,16],warranti:[15,16],web:9,websocket:9,well:[10,11],went:11,were:[0,19],what:[12,15,17],wheel:14,when:[0,5,14,18,19],where:[0,5,9,10,11,14,16,18],whether:[3,5,6,15,16,18],which:[0,3,6,7,10,11,14,15,16,18,19],whitespac:14,whooop:14,whose:13,why:14,within:[2,3,5,10],without:[7,10,11,15,16,19],wizard:16,won:[11,15,16],word:9,work:[13,16],worri:[7,15],would:[5,16,18],wouldn:16,wrap:11,wrapper:19,write_to:14,written:[9,15,16],wrong:[2,3],yaml:14,year:11,yet:13,yield:[2,3,5],you:[0,1,5,7,8,10,11,13,14,15,19],your:[7,9,14,19],yourself:5,zero:7,zih:[15,16],zzz:13},titles:["Common client operation","Drain","Exceptions","History Client","API Reference","Miscellaneous","Sink","Source","Subscriber","Glossary","Building a MetricQ Drain","Fetching historical metric data","How to use this library","Metric lookup","Creating a new project for MetricQ","Building a MetricQ Sink","Building a MetricQ Source","Welcome to MetricQ\u2019s documentation!","Metric Metadata","Upgrading <code class=\"docutils literal notranslate\"><span class=\"pre\">metricq</span></code>"],titleterms:{"class":19,"new":[14,15,16],aggreg:[5,11],ambigu:19,api:4,buffer:10,build:[10,14,15,16],chang:19,chunk:19,client:[0,3],command:14,common:0,complet:[15,16],connect:11,constant:16,content:[4,17],creat:14,data:[10,11],defin:[15,16],depend:14,deprec:19,develop:14,document:17,drain:[1,10],durat:5,exampl:[15,16],except:[2,19],fetch:11,field:18,from:17,get:11,glossari:9,handl:5,histor:11,histori:3,how:12,improv:16,indic:17,infix:13,instal:[14,17],integr:19,interfac:14,intervalsourc:16,last:11,librari:12,line:14,lint:14,locat:19,lookup:13,metadata:[11,14,18],method:19,metric:[10,11,13,18],metricq:[10,14,15,16,17,19],miscellan:5,multipl:11,network:11,older:17,oper:0,option:14,packag:14,pair:5,prefix:13,previous:19,project:14,python:19,quickstart:17,rate:16,raw:11,receiv:10,reduc:19,refer:4,regex:13,remov:19,requir:19,reserv:18,rpc:5,run:[15,16],runtim:14,search:13,setup:14,sink:[6,15],size:19,sourc:[7,16,19],standard:18,subscrib:[8,10],summar:11,system:14,tabl:17,test:14,thi:12,time:5,timeaggreg:19,timedelta:5,timestamp:5,type:19,upgrad:[17,19],use:12,using:[15,16],valid:19,valu:[5,11],version:[14,17,19],welcom:17,what:10}})