<template>
  <div class="search">
    <div class="content">
       <div class="wrapper">
        <input type="text" name="search" v-model="search_val"  :placeholder="placeHolder"
          @keydown="handleKeyDown" 
          @dblclick="handleDoubleClick" 
          @blur="handleBlur"  
          @focus="handleFocus"
          @input="handleInput" autocomplete="off"/>  
        <div class="auto_completed" v-if="showList && result_items.length > 0">
           <ul v-for="(item,i) in result_items" :key="item.id" @mousemove="mousemove(i)" :class="{'active': i === focusList }">
            <li class='show_title' @click.prevent="selectedItem(item)">{{item.name}}</li>
           </ul>
        </div>
      </div>
    </div> 
  </div>
</template>
<script>
import HTTP from "@/core/fetch"
export default {
  name: 'common-search',
  props: {
    url: {
      type: String,
      required: true
    },
    placeHolder: {
      type: String,
      required: false
    },
    searchCallback: {
      type: Function,
      required: false
    },
    searchKeyName: {
      type: String,
      required: false,
      default: 'name'
    }
  },
  data () {
    return {
      search_val: '',
      showList: true,
      focusList: '',
      result_items: []
    }
  },
  mounted () {
  },
  methods: {
    search () {
      if(this.search_val === '') {
        this.result_items = []
        return
      }
      this.axios.get(`${this.url}/_search?q=${this.searchKeyName}.pinyin:${this.search_val}`).then((dt) => {
        const data = dt.data && dt.data.hits && dt.data.hits.hits 
        if(data && data.length > 0) {
          this.result_items = data.map(item => item._source)
        } else {
          this.result_items = []
        }
      })
    },
    handleInput (e) {
      //const { value } = e.target
      this.showList = true;
      // If Debounce
      return this.search()
    },
    handleKeyDown (e) {
      let key = e.keyCode;
        // Disable when list isn't showing up
      if(!this.showList) return;
      // Key List
      const DOWN = 40
      const UP = 38
      const ENTER = 13
      const ESC = 27
      // Prevent Default for Prevent Cursor Move & Form Submit
      switch (key) {
        case DOWN:
          e.preventDefault()
          // console.log('down')
          this.focusList++;
          break;
        case UP:
          e.preventDefault()
          // console.log('up')
          this.focusList--;
          break;
        case ENTER:
          e.preventDefault()
          this.selectedItem(this.result_items[this.focusList])
          this.showList = false;
          break;
        case ESC:
          this.showList = false;
          break;
      }
      const listLength = this.result_items.length - 1;
      const outOfRangeBottom = this.focusList > listLength
      const outOfRangeTop = this.focusList < 0
      const topItemIndex = 0
      const bottomItemIndex = listLength

      let nextFocusList = this.focusList
      if (outOfRangeBottom) nextFocusList = topItemIndex
      if (outOfRangeTop) nextFocusList = bottomItemIndex
      this.focusList = nextFocusList

    },
    selectedItem (item) {
      this.search_val = item.name
      if(this.searchCallback) {
        this.searchCallback(item)
      }
    },
    handleDoubleClick(){
        this.result_items = []
        this.search()
        this.showList = true;
    },

    handleBlur(e){
        setTimeout(() => {
          this.showList = false;
        },250);
    },

    handleFocus(e){
        this.focusList = 0;
    },
    mousemove(i){
        this.focusList = i;
    },
    
  },
  components: {}
}
</script>
<style  scoped>
.search {
  padding: 0px 0px 20px 0px;
}
.search .title {
  padding: 10px 0px;
  font-size: 2em;
}
/* .search .content {
  padding: 10px 0px;
} */
.search .wrapper {
  position: relative;
  margin: 0px auto;
  width: 100%;
}
.search .wrapper > input {
  width: 100%;
  padding: 12px 10px;
  box-sizing: border-box;
  border: 1px solid #555;
  background-image: none;
  outline: none;
  font-size: 18px;
  -webkit-appearance: none;
  transition: border-color .2s cubic-bezier(.645,.045,.355,1);
  border-radius: 0px;
}
.search .wrapper > .auto_completed {
  z-index: 10000;
  position: absolute;
  left: 0px;
  top: 47px;
  width: 100%;
  min-height: 200px;
  background-color: #fff;
  border: solid 1px lightgray;
} 
.auto_completed ul {
  margin: 0px;
  padding: 0px;
  display: flex;
  flex-wrap: wrap;
  text-align: left;
}
.auto_completed ul > li{
  list-style: none;
  padding: 5px 5px;
  display: flex;
  align-items: flex-end;
  font-size: 16px;
}
li.show_title {
  color: #434343;
}
ul.active {
  background-color: lightyellow;
  cursor: pointer;
}
ul.active > li{
  color: blue;
  text-decoration: underline;
}

</style>

