import React, {  useEffect, useState , useRef} from 'react';
import Button from 'react-bootstrap/Button';
import { Dropdown } from 'react-bootstrap';
import CategoryButtonListEdit from "./CategoryButtonListEdit";
import CategoryButtonListDelete from "./CategoryButtonListDelete";
import CategoryButtonListActivities from "./CategoryButtonListActivities";

function CategoryButtonList(props){

	const setCategory = props.handler;
	const cancelCategory = props.c_handler;
	const defChangeHandler = props.def_change_handler;

	const [cid, setCid] = useState(0);
	const [showEdit, setShowEdit] = useState(false);
	const [showActivities, setShowActivities] = useState(false);
	const [showDelete, setShowDelete] = useState(false);
	const [showMenu, setShowMenu] = useState(false);
	const [position, setPosition] = useState({ x: 0, y: 0 });
	const menuRef = useRef(null);

	const [evhandle, setEvHandle] = useState(false);
	
	const handleContextMenu = (e) => {
		//console.log(e);
		e.preventDefault(); // デフォルトの右クリックメニューを無効化
		setCid(Number(e.target.value));
		setShowMenu(true);
		setPosition({ x: e.pageX, y: e.pageY });
	};

	const handleReleaseContextMenu = (e) =>{
		e.preventDefault(); 
	}

	  // メニューアイテムのクリックハンドラー
	const handleMenuItemClick = (action) => {
		alert(`${action} が選択されました。`);
		setShowMenu(false);
	};

	//編集用Modalの表示
	const handleEdit = () =>{
		setShowMenu(false);
		setShowEdit(true);
	}

	//登録アクティビティ一覧Modalの表示
	const handleActivities = () =>{
		setShowMenu(false);
		setShowActivities(true);
	}

	//削除用Modalの表示
	const handleDelete = () =>{
		setShowMenu(false);
		setShowDelete(true);
	}

	//カテゴリーIDを指定して、カテゴリーのリストからオブジェクトを取り出す
	const getCategory = (categories, cid) =>{
		//console.log("cid -",cid);
		//console.log(categories);
		//console.log(categories.find(category => category['id'] === cid));
		if(cid == 0 || cid == undefined){
			return categories[0];
		} else {
			return categories.find(category => category['id'] === cid);
		}
	}

// メニュー外をクリックしたときに非表示にする
	useEffect(() => {

		//console.log("use effect called",props.def['categories']);
		if(!evhandle){
			const handleOutsideClick = (e) => {
			if (menuRef.current && !menuRef.current.contains(e.target)) {
				setShowMenu(false);
			}
			};

			document.addEventListener('click', handleOutsideClick);
			return () => {
			document.removeEventListener('click', handleOutsideClick);
			};
			setEvHandle(true);
	}
	}, [props]);



// カテゴリーごとにボタンを定義された色を使って表示。クリック時に親モジュールから渡されたhandlerを呼び出す。
// カテゴリーボタン右クリック時にDropdownメニューを表示する。
// さらにDropdownメニューから選ばれたModal画面を表示する。

	return(
		<div className="category_button_list">
			<div className="category_button_panel">
				{props.def['categories'].map((obj) =>{
					return(
						<Button type="button" value={obj.id} class="btn btn-primary btn-sm" size="sm" 
							onClick={(e) => setCategory(e)}
							onContextMenu={(e) => handleContextMenu(e)} 
							style={{backgroundColor: obj.color, color: "white", margin: "2px"}}> {obj.name} </Button>
					)
				})}
			</div>
			<div className="cancellation_button_panel">
				<Button type="button" variant="outline-primary" class="btn btn-outline-primary btn-sm" size="sm" 
					onContextMenu={(e) =>handleReleaseContextMenu(e)} 
					onClick={(e) => cancelCategory(e)}
					style={{margin: "2px"}}> 解除 </Button>
			</div>
			{showMenu && (
				<div 
				ref={menuRef}
				style={{
					position: 'absolute',
					top: position.y,
					left: position.x,
					zIndex: 1000,
				}}
				>
					<Dropdown.Menu data-bs-theme="light" show>
						<Dropdown.Item className='fs-6' onClick={() => handleEdit()}>編集</Dropdown.Item>
						<Dropdown.Item className='fs-6' onClick={() => handleActivities()}>登録済みアクティビティ</Dropdown.Item>
						<Dropdown.Item className='fs-6' onClick={() => handleDelete()}>削除</Dropdown.Item>
					</Dropdown.Menu>
				</div>
      		)}
			
			<CategoryButtonListEdit cid={cid} show={showEdit} def_change_handler={defChangeHandler} handler={setShowEdit} categories={props.def['categories']} category={getCategory(props.def['categories'], cid)}/>
			<CategoryButtonListActivities cid={cid} show={showActivities} def_change_handler={defChangeHandler} handler={setShowActivities} categories={props.def['categories']} category={getCategory(props.def['categories'], cid)}/>
			<CategoryButtonListDelete cid={cid} show={showDelete} def_change_handler={defChangeHandler} handler={setShowDelete} categories={props.def['categories']} />
			
			</div>
	);

}

export default CategoryButtonList;