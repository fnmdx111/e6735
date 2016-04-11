$ = require 'jquery'

React = require 'react'
ReactDOM = require 'react-dom'

___css = require './lib-reqs.css'

[_btn, _img, _h2, _hr, _div, _p, _video] = (React.createFactory(name) for name in\
  ['button', 'img', 'h2', 'hr', 'div', 'p', 'video'])

VQuery = require './mods/VQuery'
VNew = require './mods/VNew'

app_view = React.createClass
  render: ->
    _div {},
      _div {id: "query-view"},
        _btn {
          id: "to-uv-btn"
          className: "btn btn-info top-right"
          type: "button"
        }, "Upload something new"
        _div {id: "query"}
      _div {id: "upload-view"},
        _btn {
          id: "to-qv-btn"
          className: "btn btn-info top-right"
          type: "query"
        }, "Query"
        _div {id: "upload"}

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
