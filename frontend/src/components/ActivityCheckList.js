import React, { useState } from 'react';
//import { getBothEnds } from "./utils"

function ActivityCheckList(props){

	// const [ev_data, setEvData]= useState(props.response);
	// const [haveData, setHaveData] = useState(false); 


	return(
		<div className="ActivityCheckList">
			<table>
				{props.response.map((obj,ix) => {		
					return (<tr style={{backgroundColor: obj['color_info']['backgroundColor'], color: obj['color_info']['stringColor']}}>
								<td width="24px"><input type="checkbox" name="a_item" data-app={obj['app']} data-title={obj['title']} value={obj['color_info']['eventId']} id={ix} /> </td> 
								<td width="120px"> <label for={ix}> {obj['app']} </label> </td>
								<td className="title_cell"  > <label for={ix}> {obj['title']}</label> </td>
								<td width="40px"> <label for={ix}> {obj['color_info']['possibility']}</label> </td>
							</tr>
							) 				
				})}
			</table>				
		</div>
		);


}

export default ActivityCheckList;