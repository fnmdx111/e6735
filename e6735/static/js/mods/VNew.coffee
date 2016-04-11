$ = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'
videojs = require 'video.js'

Uploader = React.createFactory(require './Uploader')
AbstractView = require './AbstractView'

[_span, _input, _btn, _img, _h2, _hr, _div, _p, _video, _audio, _source,
 _h4, _h5] =\
  (React.createFactory(name) for name in\
  ['span', 'input', 'button', 'img', 'h2', 'hr', 'div', 'p', 'video', 'audio',
   'source', 'h4', 'h5'])

SimplePanel = React.createFactory(require './SimplePanel')

preview_video = null

slider = React.createClass
  render: ->
    _div {className: 'col-md-6'},
      SimplePanel {title: @props.caption},
        _input {id: this.props.id, type: 'range', className: 'sliderbar'}

slider = React.createFactory slider

new_view = React.createClass
  render: ->
    $$p = this.props
    $$s = this.state ? {}

    __id = 'preview-widget'

    pv = if $$s.type?.match /video/
      _div {
        id: __id
        ref: 'target'
        className: "embed-responsive embed-responsive-16by9 mm-container"
      }
      # Because video.js is not very compatible with react.js, we are going to
      # append <video> later to this div#__id

    else if $$s.type?.match /audio/
      audio_properties =
        className: 'embed-responsive-item'
        controls: true
        preload: 'auto'
        id: 'audio-preview'

      _div {
        id: __id
        className: "embed-responsive embed-responsive-16by9 mm-container"
      },
        _audio audio_properties,
          _source {src: $$s.fp, type: $$s.type}
      # Audio tags are native HTML5 elements, work well with react.js
    else
      _div {}
      # No preview

    preview = SimplePanel {id: 'preview', title: "Preview"}, pv

    sliders = (slider {key: id, id: 'dim' + id, caption: cap} for id, cap of {
      1: 'Dim1'
      2: 'Dim2'
      3: 'Dim3'
      4: 'Dim4'
      5: 'Dim5'
      6: 'Dim6'
      7: 'Dim7'
      8: 'Dim8'
      9: 'Dim9'
      10: 'Dim10'
    })
    sliders_row = _div {className: "row"},
      sliders

    _div {},
      _div {className: 'page-header'},
        _h2 {}, "How do you like your stuff?"
      Uploader {
        url: $$p.url
        evt_hnds: $$p.evt_hnds
        auto_upload: false
      }
      _hr {className: 'vnew'}
      _div {className: "row"},
        _div {className: "col-md-8"},
          preview
        _div {className: "col-md-4"},
          sliders_row
      _div {className: "input-group"},
        _input {
          type: "text"
          className: "form-control"
          placeholder: "Title"
          id: "title-input"
          ariaDescribedby: "addon-by"
        }
        _span {className: "input-group-addon", id: "addon-by"},
          "by"
        _input {
          type: "text"
          className: "form-control"
          placeholder: "Artist"
          id: "artist-input"
          ariaDescribedby: "addon-by"
        }
        _span {className: "input-group-btn"},
          _btn {
            type: "button"
            className: "btn btn-primary pull-right"
            id: "submit"
          }, "Submit"

  componentDidUpdate: ->
    $$s = @state ? {}
    if $$s.type?.match /video/
      if not preview_video?
        wrapper = document.createElement 'div'
        wrapper.innerHTML = """<video
  id='video-preview'
  class='video-js vjs-default-skin embed-responsive-item'
  preload='auto' controls height='322' width='640'>
    <source src='#{$$s.fp}' type='#{$$s.type}' />
</video>"""

        v = wrapper.firstChild
        @refs.target.appendChild(v)
        videojs v, {}, ->
          preview_video = this
      else
        preview_video.src({
          src: $$s.fp
          type: $$s.type
        })
        preview_video.load()
        preview_video.show()

    else if $$s.type?.match /audio/
      preview_video?.reset().hide()

      a = document.getElementById('audio-preview')
      a?.load()

    true


module.exports = class VNew extends AbstractView
  constructor: (@url='/upload', anchor_id='upload') ->
    super '#' + anchor_id, anchor_id

    @evt_hnds = {
      addedfile: (file) =>
        @ra_el.setState {
          type: file.type
          fp: window.URL.createObjectURL file
        }

      init: (dz) =>
        $('#submit').on 'click', =>
          title = $('#title-input').val()
          artist = $('#artist-input').val()

          if title == ""
            alert "Title cannot be empty!"
            return
          if artist == ""
            alert "Artist cannot be empty!"
            return

          data = new FormData()
          data.append 'file', dz.files[0]
          data.append 'dims', ($('#dim' + id).val() / 100.0 for id in [1..10])
          data.append 'title', title
          data.append 'artist', artist

          $.ajax {
            url: @url
            data: data
            processData: false
            contentType: false
            type: "POST"
            success: (data) =>
              alert 'Upload successful!'
              @hide()
              @render()
          }
    }

  render: ->
    super()

    @ra_el = ReactDOM.render React.createElement(new_view, {
      url: @url
      evt_hnds: @evt_hnds
    }), @anchor
