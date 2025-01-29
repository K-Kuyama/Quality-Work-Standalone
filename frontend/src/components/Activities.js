import React, { useState } from 'react';

function Activities(props){
	const titles = ['開始時間','経過時間','マウス移動距離(x)','マウス移動距離(y)','キー入力','スクロール','アプリ','タイトル'];
	//const params = ['start_time','duration', 'distance_x', 'distance_y', 'strokes', 'scrolls','app', 'title'];
	//const [lst, setList] = useState([])
	
	if(props.response){
		return(
			<div className="activities">
				<table>
					<tr>
						{titles.map((title) => {
							return <th>{title}</th>;
						})}
					</tr>

					{props.response.map((obj) => {
						return (<tr>
									<td width="12%"> {obj['start_time']} </td>
									<td width="5%"> {obj['duration']} </td>
									<td width="9%"> {obj['distance_x']} </td>
									<td width="9%"> {obj['distance_y']} </td>
									<td width="5%"> {obj['strokes']} </td>
									<td width="5%"> {obj['scrolls']} </td>
									<td width="10%"> {obj['app']} </td>
									<td  className="title_cell"> {obj['title']} </td>
					 	</tr>);	
					})}		
				</table>
			</div>
		
		);
	}
	else return null;
}

export default Activities;