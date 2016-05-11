jQuery = require 'jquery'
$ = jQuery

React = require 'react'
ReactDOM = require 'react-dom'

___css = require './lib-reqs.css'

E = require './mods/Els'

VQuery = require './mods/VQuery'
VNew = require './mods/VNew'

app_view = React.createClass
  render: ->
    E.div {},
      E.div {id: "query-view"},
        E.btn {
          id: "to-uv-btn"
          className: "btn btn-info top-right"
          type: "button"
        }, "Upload something new"
        E.div {id: "query"}
      E.div {id: "upload-view"},
        E.btn {
          id: "to-qv-btn"
          className: "btn btn-info top-right"
          type: "query"
        }, "Query"
        E.div {id: "upload"}

  componentDidMount: ->
    $$p = this.props

    uv_btn = $ '#to-uv-btn'
    qv_btn = $ '#to-qv-btn'

    $$p.query_view.refresh_refs()
    $$p.upload_view.refresh_refs()
    $$p.query_view.render()
    $$p.upload_view.render()
    $$p.upload_view.hide(false)

    uv_btn.show()
    qv_btn.hide()

    uv_btn.on 'click', ->
      $$p.query_view.hide(false)
      $$p.upload_view.show()
      uv_btn.hide()
      qv_btn.show()

    qv_btn.on 'click', ->
      $$p.upload_view.hide(false)
      $$p.query_view.show()
      uv_btn.show()
      qv_btn.hide()

    @setState {url: '/htg-query'}

app_el = React.createElement app_view, {
  query_view: new VQuery
  upload_view: new VNew
}

ReactDOM.render app_el, document.getElementById('app-view')
