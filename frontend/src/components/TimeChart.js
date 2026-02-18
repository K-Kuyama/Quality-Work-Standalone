import React, { useState, useEffect ,useContext} from 'react';
import { getBothEnds } from "./utils";
import { ja } from "date-fns/locale";
import Settings from "../Settings";
import { ShowPolicyContext } from '../Context';

import TimeChartOption from "./TimeChartOption";

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
    //TooltipPositionerMap,
    //ChartOptions
  } from "chart.js";
  
  import { Bar } from "react-chartjs-2";
  //import ChartDataLabels from "chartjs-plugin-datalabels";
  import "chartjs-adapter-date-fns";
  
  ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    //ChartDataLabels,
    TimeScale
  );


  // グラフ描画用のデータフォーマットに加工する
  function createData(time_list){
	let data_list = []
	//let n=1;
	let first_stack = true;
	let last_date = 0;
	let color = 'rgba(53, 162, 235, 0.5)'
	time_list.map((wt) => {
		let s =0;
		let e =0;
		let sd = new Date(wt['start_time'])
		let ed = new Date(wt['end_time'])
		if(first_stack){
			s = sd.getTime();
			e = ed.getTime();
			last_date = e;
			first_stack = false;
		}
		else{
			s = sd.getTime() - last_date;
			e = ed.getTime() - last_date;
			last_date = ed.getTime();
		}

		let st = wt['start_time'].substr(11,8);
		let et = wt['end_time'].substr(11,8);
		if (wt['color'] != ""){
			color = wt['color']
		}
		else{
			color = 'rgba(53, 162, 235, 0.5)'
		}
		let w = {label: wt['title'], data:[[s,e, st+"-"+et]],skipNull: true, backgroundColor: color, stack: "_Stack0",
		datalabels: {
	      formatter: () => ""
	    }
		};
		data_list.push(w)
		//n++;
	})
	return {labels:[""], datasets: data_list};
}

// 時間文字列から経過ミリ秒を作って返す
function getET(txt){
	let d = new Date(txt);
	return d.getTime();
}


// グラフ描画用オプションを作成して返す
function getOptions(data, st, et, p_id, adjastable){
    let step = 14400;
    let resp = true; 
    if (adjastable){
        step = 1800;
        //resp = false;
    }
	const options = {
	  maintainAspectRatio: false,
      responsive: resp,
   	  //responsive: ()=>{return adjastable ? false : true;},
	  indexAxis: "y",
	  plugins: {
	    tooltip: {
	      callbacks: {
	        title: () => "",
	        afterBody: (items) =>
	          data.datasets[items[0].datasetIndex].data[items[0].dataIndex][2],
	        label: (item) => data.datasets[item.datasetIndex].label
	      },
	    },
	    legend: {
	      display: false
	    },
	    title: {
	      display: true,
	      text: "Timeline"
	    },
	    datalabels: {
	      //color: "black",
	      //anchor: "start",
	      //align: "right",
	      display: (context) => {
	        return context.dataset.data[context.dataIndex] !== null
	          ? "auto"
	          : false;
	      },
	    }
	  },
	  resizeDelay: 20,
	  //responsive: true,
	  scales: {
	    x: {
	      min: getET(st),
	      max: getET(et),
	      ticks: {
	        autoSkip: true,
	        stepSize: step,
            //stepSize: ()=>{return adjastable ? 1800 : 14400;},
            color: "#808080"
	      },
          grid:{
            color: "#808080"
          },
	      type: "time",
	      time: {
	        displayFormats: {
	          millisecond: "HH:mm:ss",
	          second: "HH:mm:ss",
	          minute: "yyyy-MM-dd HH:mm:ss",
	          hour: "yyyy-MM-dd HH:mm:ss",
	          day: "yyyy-MM-dd HH:mm:ss",
	          week: "yyyy-MM-dd HH:mm:ss",
	          month: "yyyy-MM-dd HH:mm:ss",
	          quarter: "yyyy-MM-dd HH:mm:ss",
	          year: "yyyy-MM-dd HH:mm:ss"
	        },
	        unit: "second"
	      },
	      adapters: {
	        date: {
	          locale: ja
	        }
	      },
	      stacked: true
	    },
	    y: {
          grid:{
                color: "#808080"
          },
	      stacked: true
	    },
        // xAxesgridLines:{
        //      color: "#fffffb"
        //  },
        // yAxesgridLines:{
        //     color: "#fffffb"
        // }
	  }
	};
    //console.log(options);
	return options;
}



// メイン関数

function TimeChart(props){

	const [target_date, setDate] = useState(props.target_date);
	const [g_data, setData] = useState({});
	const [g_options, setOptions] = useState({});
	const [haveData, setHaveData] = useState(false);

	const [p_id, setPid] = useState(undefined);
    const [from_to, setFromTo] = useState([])

	const ctx = useContext(ShowPolicyContext)

   useEffect(() => {
   		setDate(props.target_date);
   		setPid(props.p_id);
   		if(props.target_date){
			let date = new Date(props.target_date);
			let both_ends = getBothEnds(date, props.kind_of_period);		// OK
			let d1 = both_ends[0];
			let d2 = both_ends[1];
			let policy = ctx.policy
			let params = {start : d1, end : d2, show_policy : policy};
			//if(props.p_id){
			//	params = {start : d1, end : d2, p_id : props.p_id};
			//}
			let query = new URLSearchParams(params);

			let target = Settings.HOME_PATH+'/api/Activity/working_time_chart/?'
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/working_time_chart/?'
			}
						
			fetch(target + query	
			)
			.then(response => {
				return response.json();
			})
			.then(result =>{
				const txt = JSON.stringify(result, null,' ');
				//console.log('---Success ---');
				//console.log(txt);
				let res = JSON.parse(txt);
				if(res.length > 0){
					setFromTo([res[0].start_time, res[res.length-1].end_time]);
					//console.log("set from_to :", [res[0].start_time, res[res.length-1].end_time])
					let dt = createData(res);
					//console.log(dt);
					//let dts = getData()
					//console.log(dts);
					setData(dt);
					setOptions(getOptions(dt, d1, d2, props.p_id, false));
				}
				setHaveData(true);
			})
			.catch(error =>{
				setHaveData(false);
				console.error('----Error---');
				console.error(error);
			})
		}
    }, [props]);



	if(haveData){
        if(Settings.FULL_FUNCTIONS){
            return(
                <div className="time_chart">
                    <div className="tgraph">
                        <Bar options={g_options} data={g_data}  />
                    </div>
                    <TimeChartOption target_date={target_date} from_to={from_to} p_id={p_id} />
                </div>
            );
        } else {
            return(
                <div className="time_chart">
                    <div className="tgraph">
                        <Bar options={g_options} data={g_data}  />
                    </div>
                </div>
            );
        }
        
        
	}
	else{
		return(
			<div>loading...</div>
		)
	}
     

}

export default TimeChart;

export {getOptions, createData};

  
