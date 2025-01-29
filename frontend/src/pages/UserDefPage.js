import React, { useState } from 'react';
import PerspectivePanel from "../components/PerspectivePanel"
import PerspectiveEditor from "../components/PerspectiveEditor"

function UserDefPage(){

	const [p_id, setId] = useState(0)
//	const [def, setDef]= useState(props.data);  /* perspectiveの設定情報 */
//	const [haveData, setHaveData] = useState(false); 
	const [changed, setChanged] = useState(false);
	
	const setParam = (v) =>{
		//console.log("setParam called")
		//console.log(v)
		setId(v)
		//console.log(p_id)
	}
	
	const getParam =() =>{return p_id}

	const handleChangePerspective = (id) =>{
		//console.log("handle change perspective called : id=",id);
		setId(id);
		setChanged(true);
	}

	//console.log("UserDef p_id",p_id)

	return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls">
					<PerspectivePanel handler={setParam} get_handler={getParam} set_check={setChanged} />
				</div>
			</div>
			<div className="contents">
				<PerspectiveEditor p_id={p_id} handler={handleChangePerspective}/>
			</div>
		</div>
	)

}

export default UserDefPage;