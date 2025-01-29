import React, { useState } from 'react';
import CategorizedViewPanel from "../components/CategorizedViewPanel"
import CategoryGraph from "../components/CategoryGraph"


function CategorizedViewPage(props){

    const [target_date, setDate] = useState();
	const [p_ids, setIds] = useState([])
//	const [def, setDef]= useState(props.data);  /* perspectiveの設定情報 */
//	const [haveData, setHaveData] = useState(false); 
//	const [changed, setChanged] = useState(false);
	




	//useEffect(() =>{
    //	console.log("target_date :: ", target_date);
	//	console.log("p_ids :: ", p_ids);
    //},[target_date, p_ids])
	


	//console.log("UserDef p_ids",p_ids)

	return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls">
					<CategorizedViewPanel date_handler={setDate} ids_handler={setIds} />
				</div>
			</div>
			<div className="pie_graph_contents">
				{p_ids.map((p) => {
					return (
							<CategoryGraph p_id={p[0]} p_name={p[1]} target_date={target_date} />
						)
				})}
			</div>
		</div>
	)

}

export default CategorizedViewPage;