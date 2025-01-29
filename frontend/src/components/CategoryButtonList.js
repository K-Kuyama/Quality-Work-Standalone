//import React, {  useEffect } from 'react';
import Button from 'react-bootstrap/Button';

function CategoryButtonList(props){

	const setCategory = props.handler;
	const cancelCategory = props.c_handler;

//	useEffect(() =>{
//		console.log("=== props.def =>", props.def['categories']);
//	},[props])

	return(
		<div className="category_button_list">
			<div className="category_button_panel">
				{props.def['categories'].map((obj) =>{
					return(
						<Button type="button" value={obj.id} class="btn btn-primary btn-sm" size="sm" onClick={(e) => setCategory(e)}
							style={{backgroundColor: obj.color, color: "white", margin: "2px"}}> {obj.name} </Button>
					)
				})}
			</div>
			<div className="cancellation_button_panel">
				<Button type="button" class="btn btn-outline-primary btn-sm" size="sm" onClick={(e) => cancelCategory(e)} 
					style={{margin: "2px"}}> 解除 </Button>
			</div>
		</div>
	)

}

export default CategoryButtonList;