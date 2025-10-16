import React, { useState, useEffect, useContext } from 'react';
import Cookies from "universal-cookie";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Button from 'react-bootstrap/Button';
import 'bootstrap/dist/css/bootstrap.min.css';

import ActivityListPage from "../pages/ActivityListPage";
import AllGraphsPage from "../pages/AllGraphsPage";
import { ShowPolicyContext } from '../Context';
import Settings from "../Settings";

const cookies = new Cookies();

function NavigationMenu(props){
    const ctx = useContext(ShowPolicyContext);
    const [username, setUser] = useState(null);

    useEffect(() => {
        // ユーザー名を取得する
        if(Settings.DEVELOP){
            return
        }
        if(Settings.FULL_FUNCTIONS){
            const token = cookies.get('csrftoken')
            //console.log("csrftoken:", token);
            fetch(Settings.HOME_PATH+"/account/api-whoami",{
                        credentials: "same-origin",
                    }
            )
            .then(response => {
                return response.json();
            })
            .then(result =>{
                const txt = JSON.stringify(result, null,' ');
                //console.log('---Success ---');
                //console.log(txt);
                let res = JSON.parse(txt);
                setUser(res['username'])
            })
        }
    },[])

    
    useEffect(() =>{
        // システム設定値を取得する
        let target = Settings.HOME_PATH+'/api/SystemSettings/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/SystemSettings/'
        }

        fetch(target,{
            credentials: "same-origin",
        })
        .then(response => {
            return response.json();
        })
        .then(result =>{
            const p = Number(result[0]['audio_activity_policy']);
            ctx.updatePolicy(p);
        })    
    },[])

    const logout = (e) =>{
        let LO_PATH="/api/logout/";
        if(Settings.DELEGATION){
            LO_PATH="/api/d_logout/";
        } 

        const token = cookies.get('csrftoken')
        //console.log("token:", token);
        let target = Settings.HOME_PATH
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH
        }
        fetch(target+LO_PATH, {
			method : "POST",
			credentials: "same-origin",
			headers: {
			    'Content-Type' : 'application/json',
			    'X-CSRFToken': token,
			},
		}
		)
		.then((response) =>{
		    console.log(response);
            if(!Settings.DELEGATION){
		        window.location.href=response.url;
            }else {
                setUser(null);
            }
		})
		.catch(error =>{
			console.error(error);
		})

    }


    const login = (e) =>{
        const token = cookies.get('csrftoken')
        console.log("token:", token);
        fetch(Settings.HOME_PATH+"/api/d_login", {
			method : "POST",
			credentials: "same-origin",
			headers: {
			    'Content-Type' : 'application/json',
			    'X-CSRFToken': token,
			},
		}
		)
		.then((response) =>{
		    //console.log(response);
            setUser(response.username);
		})
		.catch(error =>{
			console.error(error);
		})
    }


    if (Settings.FULL_FUNCTIONS) {    
        //console.log(s_context.policy);
        //console.log(ctx);    
        return(
            <Navbar expand="lg" className="bg-body-tertiary"  data-bs-theme="dark">
                    <Container>
                        <Navbar.Brand href="#home">QT {username}</Navbar.Brand>
                        {/* <div className="username"> {username} </div> */}
                        <Navbar.Toggle aria-controls="basic-navbar-nav" />
                        <Navbar.Collapse id="basic-navbar-nav">
                            <Nav className="mr-auto">            	
                                <Nav.Link href={Settings.HOME_PATH+"/dashboard"}>ダッシュボード</Nav.Link>
                                <NavDropdown title="アクティビティリスト" id="activities-dropdown">
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/"}>アクティビティ</NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/audios"}>音声アクティビティ</NavDropdown.Item>   
                                </NavDropdown>                         
                                <NavDropdown title="データグラフ" id="basic-nav-dropdown">
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/date_graphs"}> 日次集計情報 </NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/week_graphs"}> 週次集計情報 </NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/month_graphs"}> 月次集計情報 </NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/year_graphs"}> 年次集計情報 </NavDropdown.Item>
                                    <NavDropdown.Divider />
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/all_graphs"}> 総合時間情報 </NavDropdown.Item>
                                </NavDropdown>
                                <NavDropdown title="カテゴリーグラフ" id="category-nav-dropdown">
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/categorize"}> 分類集計情報 </NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/multi_categorize"}> 複合分類集計情報 </NavDropdown.Item>  
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/bar_graphs"}> 総合時間情報</NavDropdown.Item>                              
                                </NavDropdown>
                                <Nav.Link href={Settings.HOME_PATH+"/editor"}>カテゴリーエディター</Nav.Link> 
                                
                                <Nav.Link href={Settings.HOME_PATH+"/settings"}>設定</Nav.Link>
                                <Nav.Link href={Settings.HOME_PATH+"/eval"}>AI評価</Nav.Link>
                                {/*
                                <NavDropdown title="データベース" id="category-nav-dropdown">
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/data_and_files"}>データアップロード</NavDropdown.Item>
                                    <NavDropdown.Item href={Settings.HOME_PATH+"/db_migration"}>DBマイグレーション</NavDropdown.Item>
                                </NavDropdown>
                                */}
                                
                            </Nav>
                            <Button className="logout-button" variant="secondary" size="sm" style={{marginLeft: "2px"}} onClick={logout} id="loButton">ログアウト <i class="bi bi-box-arrow-right"></i></Button>
                        </Navbar.Collapse>
                    </Container>
                    
            </Navbar>	
        );
    } else {
        return(
            <Navbar expand="lg" className="bg-body-tertiary"  data-bs-theme="dark">
                    <Container>
                        <Navbar.Brand href="#home">QT</Navbar.Brand>
                        {/* <div className="username"> {username} </div> */}
                        <Navbar.Toggle aria-controls="basic-navbar-nav" />
                        <Navbar.Collapse id="basic-navbar-nav">
                            <Nav className="mr-auto">            	
                                <Nav.Link href={Settings.HOME_PATH+"/dashboard"}>ダッシュボード</Nav.Link>
                                <Nav.Link href={Settings.HOME_PATH+"/"}>アクティビティリスト</Nav.Link>   
                                <Nav.Link href={Settings.HOME_PATH+"/all_graphs"}>グラフ</Nav.Link>                       
                            </Nav>
                        </Navbar.Collapse>
                    </Container>
                    
               </Navbar>	
        );
    }


}

export default NavigationMenu;