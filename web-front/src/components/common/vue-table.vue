<template>
<div>
  <table :class="className">
    <thead>
      <th v-for="item in columns" @click="order(item)">{{item.title}}<i v-if="orderBy == item.name"  :class="{'fa fa-sort-desc': isDesc, 'fa fa-sort-up': isAsc }" /></th>
    </thead>
    <tbody>
      <div v-if="showLoad"><img src="~assets/images/loading.gif" style="width: 40px;height: 40px;"/></div>
      <tr v-for="row in rows" @click="selectedRow(row, $event)">
        <td v-for="col in columns" :class="col.class ? col.class : col.type">
          <template v-if="col.type != 'attention' && col.type != 'stockcode' && col.type != 'holder'">
          {{formatColVal(row, col)}}
          </template>
          <template v-else-if="col.type =='stockcode'">
            <a :href="buildStockUrl(row, col)" @click.stop="empty" target="_blank">{{formatColVal(row, col)}}</a>
          </template>
          <template v-else-if="col.type =='holder'">
            <a @click.stop="navigateToHolders(row, col)"  target="_blank">{{formatColVal(row, col)}}</a>
          </template>
          <template v-else>
            <i @click.stop="attention(row,col)" :class="{'fa fa-heart': row[col.name] === true, 'fa fa-heart-o': row[col.name] !== true}"></i>
          </template>
        </td> 
        <td v-if="operations != null && operations.length > 0" class="vtbOperations">
          <span v-for="opt in operations" v-bind:key="opt.title" v-if="opt.isShow(row)">
            <a @click.stop="opt.callback(row)">{{opt.title}}</a>
          </span>
        </td>
      </tr>
    </tbody>
  </table>
  <pagination v-if="showPagerCtl" :pageInfo="pageInfo" @change="pagechange"></pagination>
</div>
</template>
<script>
import Pagination from '@/components/common/vue-pagination'
import HTTP from "@/core/fetch"
import $ from 'jQuery'
import Numeral from 'numeral'

export default {
  name: 'vue-table',
  props: {
    url: {
      type: String,
      required: true
    },
    className: {
      type: String,
      require: false
    },
    showPager: {
      type: Boolean,
      require: false
    },
    operations: {
      type: Array,
      require: false
    }
  },
  data () {
    return {
      columns: [],
      rows:    [],
      orderBy: '',
      orderDirect: '',
      loadUrl: this.url,
      lastUpdate: null,
      showPagerCtl: this.showPager === true,
      pageInfo:{},
      showLoad: false
    }
  },
  mounted () {
    this.loadData()
  },
  methods: {
    loadData (queryParams) {
      if(this.loadUrl) {
        if (typeof(queryParams) === 'undefined') {
          queryParams = ''
        }
        let targetUrl = this.loadUrl
        if(queryParams !== '') {
          if(this.loadUrl.indexOf('?') >= 0) {
            targetUrl = `${this.loadUrl}&${queryParams}`
          } else {
            targetUrl = `${this.loadUrl}?${queryParams}`
          }
        }
        HTTP.get(targetUrl).then((dt) => {
          this.orderBy     = dt.data.orderBy 
          this.orderDirect = dt.data.orderDirect
          if(this.columns.length === 0 || this.columns.length !== dt.data.columns.length) {
            this.columns   = dt.data.columns
          }
          this.rows        = dt.data.list
          if(this.lastUpdate == null || dt.data.lastUpdate != this.lastUpdate) {
            this.lastUpdate  = dt.data.lastUpdate
            this.$emit('onLastUpdated', this.lastUpdate)
          }
          this.pageInfo = dt.data.pagination
                  
          this.$emit('onDataLoadCompeleted', dt.data)

        })
      } else {
        this.rows = []
      }
    },
    order (col) {
      if(typeof col.sortable !== 'undefined' && col.sortable === false) {
        return
      }
      let colname = col.name
      let direct = ''
      if (colname === this.orderBy) {
        if (this.orderDirect === 'asc') {
          direct = 'desc'
        } else {
          direct = 'asc'
        }
      } else {
        direct = 'asc'
      }
      this.loadData('orderBy=' + colname + '&orderDirect=' + direct)
      $(this.$el).find('tr').removeClass('selected')
      this.$emit('onDataChange')
    },
    afterProcess () {
      //process stock code 
      // const self = this
      // $(this.$el).find('td.percent').each((i,item) => {
      //   const val = parseFloat($(item).html().replace('%', ''))
      //   if(val > 0) {
      //     $(item).addClass('red')
      //   }
      //   if(val < 0) {
      //     $(item).addClass('green')
      //   }
      //   console.log(val)
      // })

    },
    formatColVal (row, col) {
      switch(col.type) {
        case 'numeric':
          return Numeral(row[col.name]).format('0,0')          
        case 'percent':
          if(col.hasPercented) {
            return `${row[col.name]}%`
          } else {
            return Numeral(row[col.name]).format('0.00%')     
          }
        case 'code':
          const val = row[col.name]
          if(val.length === 5) {
            return `${val}.HK`
          } else {
            return val
          }
        case 'stockcode':
          const sval = row[col.name]
          if(sval.length === 5) {
            return `${sval}.HK`
          } else {
            return sval
          }
        default:
          return row[col.name]
      }
    },
    buildStockUrl (row, col) {
      const firstChar = row[col.name][0]
      const code = (firstChar === '5' || firstChar === '6' || firstChar === '9') ? `SH${row[col.name]}` : `SZ${row[col.name]}`
      if(row[col.name].length > 5) {
        return `https://xueqiu.com/S/${code}`
      }  else {
        return `https://xueqiu.com/S/${row[col.name]}`
      }
    },
    selectedRow (row, e) {
      $(e.target).parent().parent().find('tr').removeClass('selected')
      $(e.target).parent().addClass('selected')
      this.$emit('onRowSelected', row)
    },
    pagechange (page) {
      this.loadData('orderBy=' + this.orderBy + '&orderDirect=' + this.orderDirect + '&page=' + page)
      this.$emit('onDataChange')
      $(this.$el).find('tr').removeClass('selected')
    },
    attention (row, col) {
      console.log(row, col)
      if(row[col.name] === true) {
        HTTP.delete(`/hkmainland/attention?code=${row.stockcode}`).then(dt => {
          console.log(dt.data)
          row[col.name] = false
        })
      } else {
        HTTP.post(`/hkmainland/attention?code=${row.stockcode}`).then(dt => {
          console.log(dt.data)
          row[col.name] = true
        })
      }
      
    },
    navigateToHolders (row, col) {
      console.log(row, col)
      this.$router.push({name: 'HsgtHoldersAnalysis', params: {code: row.code, name: row.name}})
    },
    empty () {
      return true
    }
  },
  computed: {
    isAsc () {
      return this.orderDirect === 'asc'
    },
    isDesc () {
      return this.orderDirect === 'desc'
    }
  },
  components: {
    Pagination
  },
  watch : {
    url () {
      // console.log('ok........', this.url)
      this.loadUrl = this.url
      this.loadData()
      this.$emit('onDataChange')
      $(this.$el).find('tr').removeClass('selected')
    }
  }

}
</script>

<style lang="scss" scoped>
table{
  width: 100%;
}
table th:hover{
  cursor: pointer;
}
table th > i{
  margin-left: 3px;
  margin-top: 2px;
  color: darkblue;
}
table td,th{
  padding: 5px;
  text-align: center;
}
table td.holder {
  text-align: left;
}
table td.numeric{ 
}
table td.percent{ 
}
table td.attention {
  font-size: 13px;
}
table td.attention > a {
  color: grey;
}
table td.attention > a:hover {
  color: red;
}
table td.amount, td.numeric, td.buy, td.sold {
  text-align: right;
}
table td.vtbOperations {
  >span {
    padding: 0px 5px;
  }
}
.fa {
  font-size: 14px;
  cursor: pointer;
}
.fa-heart {
  color: #EC3B3F;
  &:hover {
    color: grey;
  }
}
.fa-heart-o {
  &:hover {
    font-size: 16px;
    color: #EC3B3F;
  }
}
.table > thead > tr > th, .table > tbody > tr > th, .table > tfoot > tr > th, .table > thead > tr > td, .table > tbody > tr > td, .table > tfoot > tr > td {
  // border-top: solid 1px #f1eded;
  border-top: solid 1px #EDF0F5;
}
</style>


