{% load url from future %}
var _textblock_edit_mode = false;

function get_element_by_id(element_id)
{
	return $("#"+element_id);
}
function get_element_list_by_class_name(class_name)
{
	return $("."+class_name);
}

function textblock_toggle_drag_n_drop_mode()
{
    if (_textblock_drag_n_drop_activated)
    {
        _textblock_drag_n_drop_activated = !_textblock_drag_n_drop_activated;
        get_element_by_id('textblock_drag_n_drop_toggle_button').removeClass('activated');
        _textblock_disable_dnd();
    }
    else
    {
        if (_textblock_edit_mode)
            textblock_toggle_edit_mode();

        _textblock_drag_n_drop_activated = !_textblock_drag_n_drop_activated;
        get_element_by_id('textblock_drag_n_drop_toggle_button').addClass('activated');
        _textblock_enable_dnd();
    }
}

function textblock_toggle_edit_mode()
{
    if (_textblock_edit_mode)
    {
        get_element_by_id('textblock_edit_mode_link').removeClass('activated');
        _textblock_edit_mode = false;
        get_element_list_by_class_name("edit_mode_listener").removeClass("active");
    }
    else
    {
        if (_textblock_drag_n_drop_activated)
            textblock_toggle_drag_n_drop_mode();

        get_element_by_id('textblock_edit_mode_link').addClass('activated');
        _textblock_edit_mode = true;
        get_element_list_by_class_name("edit_mode_listener").addClass("active");
    }
}

function _textblock_edit(textblock_id, url)
{
    __textblock_inline_editor(get_element_by_id('textblock_'+textblock_id).parent(), url);
    return false;
}
function _textblock_cancel_editing(textblock_id, url)
{
    __textblock_inline_editor(get_element_by_id('textblock_editing_'+textblock_id).parent(), url);
}

function __textblock_inline_editor(div, url)
{
    div.load( url);
//	div.set('load', {
//		evalScripts: true,
//		data: null
//	});
//	div.load(url);
	return false;
}

function submit_textblock_inline_form(form)
{
    _textblock_enable_dnd();
	form.getChildren('input[type="submit"], button').each(function(item, i)
	{
		item.setStyle('opacity','0.5');
		item.setAttribute('disabled',true);
		item.setAttribute('enabled',false);
	});

	form.set('send', {
		evalScripts: true,
		onSuccess: function(res) {
			form.getParent().getParent().set('html',res);
		}
	});
	form.send();
	return false;
}

function go_textblock(self, url)
{
	window.location = self.getSelected()[0].get('name');
}

function submit_textblock_template(div_id, url)
{
	var form = $("#"+div_id+" .template_form input[name='content']");
	var template = decodeURIComponent(form.val());
	$("#"+div_id+' .template_form input').each(function(field)
	{
		template = template.replace("[["+field.name+"]]", field.value);
	});
	form.val(template);
	return true;
}

function show_textblock_template_fields(self, position)
{
    var div_id = position+"_fields_"+self.getSelected()[0].get('name');

 	$(".template_fields").css('display',"none");

 	var textblock = get_element_by_id(position+"_new_textblock");

	textblock.unbind('mouseover');
	textblock.unbind('mouseout');
	textblock.removeClass("faded");
	get_element_by_id(div_id).css('display',"block");
}

function _textblock_check_drop_point(draggable, droppable)
{
    var draggable_id = draggable.get("_id");
    var droppable_id = droppable.get("_id");
    if (draggable_id == droppable_id)
        return false;
    else
        return true;
}

var _textblock_drag_n_drop_activated = false;
var _textblock_drag_n_drop_enabled = false;
var _textblock_drag_n_drop_elements = new Array();
var _textblock_is_dragging = false;
var _textblock_original_position = {x:0,y:0};

function _textblock_disable_dnd()
{
    if (_textblock_drag_n_drop_enabled)
    {
        _textblock_drag_n_drop_elements.each(function(drag) {
            drag.detach();
            drag.element.removeClass('drag_active');
        });
        _textblock_drag_n_drop_elements.empty();
        _textblock_drag_n_drop_enabled = false;
    }
}
function _textblock_enable_dnd()
{
    if (!_textblock_drag_n_drop_activated)
        return;
        
    if (!_textblock_drag_n_drop_enabled)
    {
        _textblock_drag_n_drop_enabled = true;
        $('.textblock.draggable').each(function(drag) {

            drag.addClass('drag_active');
            drag.css('top',0);
            drag.css('left',0);

            _textblock_drag_n_drop_elements.push(
                new Drag.Move(drag, { 
                    droppables: '.textblock_drop_point',
                    precalculate: false, 
                    onDrop: function(el,droppable) {
                        if (!droppable || !_textblock_check_drop_point(el, droppable))
                        {
                            el.setPosition(_textblock_original_position);
                            return;
                        }
                        var request = new Request({
                            url: '{% url "textblock_drop" %}',
                            data: "id="+drag.get('_id')+"&drop_position="+droppable.get('_position')+"&drop_sort_order="+droppable.get("_order"),
                            method: "post",
                            onSuccess: function(response)
                            {
                                window.location.reload();
                            }
                        });

                        request.send();
                    },
                    onComplete: function(el)
                    {
                        el.removeClass("being_dragged");
                        _textblock_is_dragging = false;
                        $(".textblock_drop_point").removeClass('active');
                    },
                    onCancel: function(el)
                    {
                        _textblock_is_dragging = false;
                        el.removeClass("being_dragged");
                        $(".textblock_drop_point").removeClass('active');
                    },
                    onBeforeStart: function(el)
                    {
                        _textblock_original_position = el.getCoordinates();
                        el.addClass("being_dragged");
                        if (!_textblock_is_dragging)
                        {
                            _textblock_is_dragging = true;
                            $(".textblock_drop_point").each(function(droppable)
                            {
                                if (_textblock_check_drop_point(el, droppable))
                                droppable.addClass('active');
                            });
                        }
                    },
                    onEnter: function(el,droppable) {
                        if (_textblock_check_drop_point(el, droppable))
                        {
                            droppable.addClass('over');
                        }
                    },
                    onLeave: function(el,droppable) {
                        droppable.removeClass('over');
                    }
                })
            );
        });
    }
}

window.addEvent("domready", function()
{
    document.ondragstart = function () { return false; }; //IE drag hack
});
