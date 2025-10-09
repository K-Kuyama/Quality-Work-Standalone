import React, { useState, useEffect } from 'react';
import PerspectivePanel from "../components/PerspectivePanel"
import PerspectiveEditor from "../components/PerspectiveEditor"

function UserDefPage(){

	const [p_id, setId] = useState(0)
	const [changed, setChanged] = useState(false);

	//モーダル表示用
	const [showModal, setShowModal] = useState(false);
	

	const setParam = (v) =>{
		setId(Number(v))
	}
	
	const getParam =() =>{return p_id}



	const handleChangePerspective = (st) =>{
		setChanged(st);
	}


	const setShowModalPrint = (kind) =>{
		setShowModal(kind);
	}

	return(
		<div className="app_page">
			<div className="sidebar">
				<div id="controls" className="controls">
					<PerspectivePanel handler={setParam} get_handler={getParam} set_check={setChanged} />
				</div>
			</div>
			<div className="contents">
				<PerspectiveEditor p_id={p_id} changed={changed} handler={handleChangePerspective} modal_handler={setShowModalPrint}/>
			</div>
		</div>
	)

}

export default UserDefPage;