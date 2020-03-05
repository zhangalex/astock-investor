<template>
  <div>
    <el-table :data="tableData" border stripe style="width: 100%" size="small">
        <el-table-column type="index" :index="indexMethod" align="center"></el-table-column>
        <el-table-column v-for="(col,i) in columns" v-bind:key="i" :prop="col.name" :label="col.title" :width="col.width" align="center"></el-table-column>
        <el-table-column v-if="operations && operations.length > 0" fixed="right" label="操作" width="120" align="center">
            <template slot-scope="scope">
              <el-button v-for="opt in operations" v-bind:key="opt.title" @click.native.prevent="opt.callback(tableData[scope.$index])" v-if="opt.isShow(tableData[scope.$index])" type="text" size="small">{{opt.title}}</el-button>
            </template>
        </el-table-column>
        <slot></slot>
    </el-table>
    <div class="pagerBox">
        <el-pagination layout="prev, pager, next" :page-size="pageSize" :total="totalQuantity" @current-change="onPageClick"></el-pagination>
    </div>
  </div>
</template>
<script>
  import { Message, MessageBox } from 'element-ui'
  export default {
    name: 'common-table',
    props: {
      columns: {
        type: Array,
        required: true
      },
      tableData: {
        type: Array,
        required: true
      },
      pageSize: {
        type: Number,
        required: true
      },
      totalQuantity: {
        type: Number,
        required: true
      },
      loadDataCallback: {
        type: Function,
        required: true   
      },
      operations: {
        type: Array,
        required: false
      }
    },
    data () {
      return {
      }
    },
    methods: {
      onPageClick (pageIndex) {
          this.loadDataCallback(pageIndex)
      },
      editRow (index, list) {
        if(this.editCallback) {
          this.editCallback(list[index])
        }
      },
      deleteRow (index, list) {
        const self = this
        if(this.deleteCallback) {
          MessageBox.confirm('您确实要删除该行记录吗？', '删除确认', {
                    confirmButtonText: '删除',
                    cancelButtonText: '取消',
                    type: 'warning'
           }).then(() => {
            self.deleteCallback(list[index])
          }, ()=> {console.log('You canceled')})
        }
      },
      indexMethod (index) {
        return index + 1
      }
    },
    computed: {
    }
  }
</script>
<style lang="scss">
.pagerBox {
    text-align: right;
    margin-top: 10px;
    margin-right: -5px;
}
</style>
