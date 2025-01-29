import React, { useState } from 'react';
import MultiCategorizedViewPanel from "../components/MultiCategorizedViewPanel"
import MultiCategoryGraph from "../components/MultiCategoryGraph"


function MultiCategorizedViewPage(){

    const [target_date, setDate] = useState();
    const [p_id, setPid] = useState(0)
    const [sub_p_id, setSubPid] = useState(0)
    
    //useEffect(() =>{
    //	console.log("target_date :: ", target_date);
	//	console.log("p_id :: ", p_id);
	//	console.log("sub_p_id :: ", sub_p_id);
    //},[target_date,p_id,sub_p_id])
    
	return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls">
					<MultiCategorizedViewPanel date_handler={setDate} pid_handler={setPid} spid_handler={setSubPid} />
				</div>
			</div>
			<div className="pie_graph_contents">
					<MultiCategoryGraph target_date={target_date} p_id={p_id} sub_p_id={sub_p_id} />
			</div>
		</div>
	)

}

export default MultiCategorizedViewPage;