import React from "react";
// react component for creating dynamic tables
import ReactTable from "react-table";

// @material-ui/core components
import withStyles from "@material-ui/core/styles/withStyles";
// @material-ui/icons
import Assignment from "@material-ui/icons/Assignment";
import ViewList from "@material-ui/icons/ViewList";
import Dvr from "@material-ui/icons/Dvr";
import Favorite from "@material-ui/icons/Favorite";
import Archive from "@material-ui/icons/Archive";
import Close from "@material-ui/icons/Close";
// core components
import GridContainer from "components/Grid/GridContainer.jsx";
import GridItem from "components/Grid/GridItem.jsx";
import Button from "components/CustomButtons/Button.jsx";
import Card from "components/Card/Card.jsx";
import CardBody from "components/Card/CardBody.jsx";
import CardIcon from "components/Card/CardIcon.jsx";
import CardHeader from "components/Card/CardHeader.jsx";

import { dataTable } from "variables/general.jsx";

import { cardTitle } from "assets/jss/material-dashboard-pro-react.jsx";

import { getStockList } from "../../util/Stock";
import { setPersistStore } from "../../util/Auth";

import axios from 'axios';
import { URL, STOCK_SHAREHOLDER_EXCEL_DL } from '../../config/Api';
import store from '../../store';

const styles = {
  cardIconTitle: {
    ...cardTitle,
    marginTop: "15px",
    marginBottom: "0px"
  }
};

class ReactTables extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: []
    }
    {/*this.state = {
      data: dataTable.dataRows.map((prop, key) => {
        return {
          id: key,
          name: prop[0],
          position: prop[1],
          office: prop[2],
          age: prop[3],
          actions: (
            // we've added some custom button actions
            <div className="actions-right">
              <Button
                justIcon
                round
                simple
                onClick={() => {
                  let obj = this.state.data.find(o => o.id === key);
                  alert(
                    "You've clicked LIKE button on \n{ \nName: " +
                      obj.name +
                      ", \nposition: " +
                      obj.position +
                      ", \noffice: " +
                      obj.office +
                      ", \nage: " +
                      obj.age +
                      "\n}."
                  );
                }}
                color="info"
                className="like"
              >
                <Favorite />
              </Button>{" "}
              <Button
                justIcon
                round
                simple
                onClick={() => {
                  let obj = this.state.data.find(o => o.id === key);
                  alert(
                    "You've clicked EDIT button on \n{ \nName: " +
                      obj.name +
                      ", \nposition: " +
                      obj.position +
                      ", \noffice: " +
                      obj.office +
                      ", \nage: " +
                      obj.age +
                      "\n}."
                  );
                }}
                color="warning"
                className="edit"
              >
                <Dvr />
              </Button>{" "}
              <Button
                justIcon
                round
                simple
                onClick={() => {
                  var data = this.state.data;
                  data.find((o, i) => {
                    if (o.id === key) {
                      // here you should add some custom code so you can delete the data
                      // from this component and from your server as well
                      data.splice(i, 1);
                      return true;
                    }
                    return false;
                  });
                  this.setState({ data: data });
                }}
                color="danger"
                className="remove"
              >
                <Close />
              </Button>{" "}
            </div>
          )
        };
      })
    };*/}
  }

  downloadStock(stock_id, stock_name) {
    const token = store.getState().token;
    axios.get(URL + STOCK_SHAREHOLDER_EXCEL_DL + "?stock_id=" + stock_id,
     { headers: { Authorization: 'Token ' + token } }).then(function(response){
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        //link.setAttribute('download', stock_id + "_" + stock_name + ".xlsx");
        document.body.appendChild(link);
        link.click();        
     })
  }

  componentDidMount() {
    const self = this;
    setPersistStore(
      function(){
        getStockList().then(function(d){
          console.log(d);
          self.setState({data:d.data.data.map((prop, key) => {
            return {
              id: key,
              stock_id: prop['stock_id'],
              stock_name: prop['stock_name'],
              actions: (
                <div className="actions-right">
                  <Button
                    justIcon
                    round
                    simple
                    href={URL + STOCK_SHAREHOLDER_EXCEL_DL + "?stock_id=" + prop['stock_id']}
                    target="_blank"
                    color="info"
                    className="like"
                    size="lg"
                  >
                    <Archive />
                  </Button>{" "}
                </div>
              )              
            }
          })});
      });
    });
  }

  render() {
    const { classes } = this.props;
    return (
      <GridContainer>
        <GridItem xs={12}>
          <Card>
            <CardHeader color="primary" icon>
              <CardIcon color="primary">
                <ViewList />
              </CardIcon>
              <h4 className={classes.cardIconTitle}>公司列表</h4>
            </CardHeader>
            <CardBody>
              <ReactTable
                data={this.state.data}
                filterable
                columns={[
                  {
                    Header: "股票代號",
                    accessor: "stock_id"
                  },
                  {
                    Header: "公司名稱",
                    accessor: "stock_name"
                  },
                  {
                    Header: "下載大股東EXCEL",
                    accessor: "actions",
                    sortable: false,
                    filterable: false                    
                  }                                    
                ]}
                defaultPageSize={10}
                showPaginationTop
                showPaginationBottom={false}
                className="-striped -highlight"
                previousText='上一頁'
                nextText='下一頁'
                loadingText='資料讀取中...'
                noDataText='無資料...'
                pageText='頁數'
                ofText='/'
                rowsText='筆'
              />
            </CardBody>
          </Card>
        </GridItem>
      </GridContainer>
    );
  }
}

export default withStyles(styles)(ReactTables);
